"""Lux Application class
"""
import sys
import os
import json
import asyncio
import threading
from asyncio import create_subprocess_shell, subprocess

from copy import copy
from inspect import isclass, getfile
from collections import OrderedDict
from importlib import import_module

import pulsar
from pulsar import ImproperlyConfigured
from pulsar.apps.wsgi import (WsgiHandler, HtmlDocument, test_wsgi_environ,
                              LazyWsgi, wait_for_body_middleware,
                              middleware_in_executor, wsgi_request)
from pulsar.utils.log import lazyproperty
from pulsar.utils.importer import module_attribute
from pulsar.apps.greenio import GreenWSGI, GreenHttp
from pulsar.apps.http import HttpClient
from pulsar.utils.string import to_bytes

from lux import __version__
from lux.utils.files import skipfile
from lux.utils.data import multi_pop
from lux.utils.token import encode_json

from .commands import ConsoleParser, CommandError, ConfigError, service_parser
from .extension import LuxExtension, Parameter, EventMixin, app_attribute
from .wrappers import HeadMeta, LuxContext, formreg
from .templates import render_data, template_engine, Template
from .cms import CMS
from .models import ModelContainer
from .cache import create_cache
from .exceptions import ShellError
from .channels import Channels
from .auth import SimpleBackend


LUX_CORE = os.path.dirname(__file__)


def execute_from_config(config_file, services=None,
                        description=None, argv=None,
                        cmdparams=None, **params):     # pragma    nocover
    """Create and run an :class:`.Application` from a ``config_file``.

    This is the function to use when creating the script which runs your
    web applications::

        import lux

        if __name__ == '__main__':
            lux.execute_from_config('path.to.config')

    :param config_file: the python dotted path to the config file for setting
        up a new :class:`App`. The config file should be located in the
        python module which implements the main application
        of the web site.
    """
    if services:
        p = service_parser(services, description, False)
        opts, argv = p.parse_known_args(argv)
        if not opts.service and len(argv) == 1 and argv[0] in ('-h', '--help'):
            service_parser(services, description).parse_known_args()
        config_file = config_file % (opts.service or services[0])
        if opts.service and description:
            description = '%s - %s' % (description, opts.service)

    cmdparams = cmdparams or {}
    return execute_app(App(config_file, argv=argv, **params),
                       description=description, **cmdparams)


def execute_app(app, argv=None, description=None,
                **params):  # pragma    nocover
    """Execute a given ``app``.

    :parameter app: the :class:`.App` to execute
    :parameter argv: optional list of parameters, if not given ``sys.argv``
        is used instead.
    :parameter params: additional key-valued parameters to pass to the
        :class:`.Command` executing the ``app``.
    """
    if argv is None:
        argv = app._argv
    if argv is None:
        argv = sys.argv
        app._argv = argv = list(argv)
        app._script = argv.pop(0)
    try:
        application = app.setup(handler=False)
    except ImproperlyConfigured as e:
        print('IMPROPERLY CONFUGURED: %s' % e)
        exit(1)
    # Parse for the command
    parser = application.get_parser(add_help=False, description=description)
    opts, _ = parser.parse_known_args(argv)
    #
    # we have a command
    if opts.command:
        try:
            command = application.get_command(opts.command)
        except CommandError as e:
            print('\n'.join(('%s.' % e, 'Pass -h for list of commands')))
            exit(1)
        argv = list(argv)
        argv.remove(command.name)
        try:
            return command(argv, **params)
        except CommandError as e:
            print(str(e))
            exit(1)
    else:
        # this should fail unless we pass -h
        parser = application.get_parser(nargs=1, description=description)
        parser.parse_args(argv)


def extend_config(config, parameters):
    """Extend a config dictionary with additional parameters
    """
    for namespace, cfg in parameters.items():
        # Allow one nesting
        if namespace not in config and isinstance(cfg, dict):
            for name, value in cfg.items():
                fullname = '%s_%s' % (namespace, name)
                config[fullname] = value
        else:
            config[namespace] = cfg


class App(LazyWsgi):

    def __init__(self, config_file, script=None, argv=None, config=None, **kw):
        params = config or {}
        params.update(kw)
        self._params = params
        self._config_file = config_file
        self._script = script
        self._argv = argv

    @property
    def command(self):
        return self._argv[0] if self._argv else None

    def setup(self, environ=None, on_config=None, handler=True):
        app = Application(self)
        if on_config:
            on_config(app)
        if handler:
            app.wsgi_handler()
        return app

    def clone(self, **kw):
        params = self._params.copy()
        params.update(kw)
        app = copy(self)
        app._params = params
        app._argv = copy(app._argv)
        return app


def Http(app):
    params = app.config['HTTP_CLIENT_PARAMETERS'] or {}
    green = app.green_pool
    if not green:
        params['loop'] = pulsar.new_event_loop()
    http = HttpClient(**params)
    return GreenHttp(http) if green else http


class Application(ConsoleParser, LuxExtension, EventMixin):
    """The :class:`.Application` is the WSGI callable for serving
    lux applications.

    It is a specialised :class:`~.LuxExtension` which collects
    all extensions of your application and setup the wsgi middleware used by
    the web server.
    An :class:`Application` is not initialised directly, the higher level
    :func:`.execute_from_config` or :func:`.execute_app` are
    used instead.

    .. attribute:: channels

        The :class:`.Channels` manager of this application. This attribute
        can be used to register to channels events or publish events
        on channels. For more information check the channels documentation

    .. attribute:: config

        The configuration dictionary

    .. attribute::  extensions

        Ordered dictionary of :class:`.LuxExtension` loaded into the
        application. Extensions are specified in the :setting:`EXTENSIONS`
        setting parameter
    """
    cfg = None
    channels = None
    debug = False
    logger = None
    admin = None
    _handler = None
    auth_backend = None
    forms = None
    """Form registry for this application. Add/override forms via the
    on_loaded event"""
    cms = None
    """CMS handler"""
    api = None
    """Handler for Lux API server"""
    _WsgiHandler = WsgiHandler
    _http = None
    _config = [
        Parameter('EXTENSIONS', [],
                  'List of extension names to use in your application. '
                  'The order matter since the wsgi middleware of extension is '
                  'processed in the order given by this setting.'),
        Parameter('DESCRIPTION', None,
                  'A description to display before the argument help on the '
                  'command line when running commands'),
        Parameter('COPYRIGHT', 'Lux',
                  'Site Copyright', True),
        Parameter('APP_NAME', 'Lux',
                  'Application site name', True),
        Parameter('ENCODING', 'utf-8',
                  'Default encoding for text.'),
        Parameter('SETTINGS_FILES', None,
                  'Path to a json file with additional settings'),
        Parameter('ERROR_HANDLER', 'lux.core.wrappers:error_handler',
                  'Dotted path to handler of Http exceptions'),
        Parameter('MEDIA_URL', '/media/',
                  'the base url for static files', True),
        Parameter('MINIFIED_MEDIA', True,
                  'Use minified media files. All media files will replace '
                  'their extensions with .min.ext. For example, javascript '
                  'links *.js become *.min.js', True),
        #
        Parameter('SECRET_KEY',
                  'secret-key',
                  'A string or bytes used for encrypting data. Must be unique '
                  'to the application and long and random enough'),
        #
        # HTML base parameters
        Parameter('HTML_TITLE', 'Lux',
                  'Default HTML Title'),
        Parameter('HTML_LINKS', [],
                  'List of links to include in the html head tag.'),
        Parameter('HTML_SCRIPTS', [],
                  'List of scripts to load in the head tag'),
        Parameter('HTML_REQUIREJS_URL',
                  "//cdnjs.cloudflare.com/ajax/libs/require.js/2.1.22/require",
                  'Default url for requirejs. Set to None if no requirejs '
                  'is needed by your application'),
        Parameter('HTML_META',
                  [{'http-equiv': 'X-UA-Compatible',
                    'content': 'IE=edge'},
                   {'name': 'viewport',
                    'content': 'width=device-width, initial-scale=1'}],
                  'List of default ``meta`` elements to add to the html head'
                  'element'),
        #
        # CONTENT base parameters
        Parameter('CONTENT_GROUPS', {
            "site": {
                "path": "*",
                "body_template": "home.html"
            }
        }, 'List of content model configurations'),
        Parameter('CONTENT_LINKS',
                  {'python': 'https://www.python.org/',
                   'lux': 'https://github.com/quantmind/lux',
                   'pulsar': 'http://pythonhosted.org/pulsar'},
                  'Links used throughout the web site'),
        #
        # BASE email parameters
        Parameter('EMAIL_BACKEND', 'lux.core.mail.EmailBackend',
                  'Default locale'),
        Parameter('EMAIL_DEFAULT_FROM', '',
                  'Default email address to send email from'),
        Parameter('EMAIL_DEFAULT_TO', '',
                  'Default email address to send email to'),
        #
        Parameter('ASSET_PROTOCOL', '',
                  ('Default protocol for scripts and links '
                   '(could be http: or https:)')),
        Parameter('DATE_FORMAT', 'd MMM y',
                  'Default formatting for dates in JavaScript', True),
        Parameter('DATETIME_FORMAT', 'd MMM y, h:mm:ss a',
                  'Default formatting for dates in JavaScript', True),
        Parameter('DEFAULT_TEMPLATE_ENGINE', 'jinja2',
                  'Default template engine'),
        # Cache
        Parameter('CACHE_SERVER', 'dummy://',
                  ('Cache server, can be a connection string to a valid '
                   'datastore which support the cache protocol or an object '
                   'supporting the cache protocol')),
        Parameter('CACHE_DEFAULT_TIMEOUT', 60,
                  'Default timeout for data stored in cache'),
        #
        Parameter('LOCALE', 'en_GB', 'Default locale', True),
        Parameter('DEFAULT_TIMEZONE', 'GMT',
                  'Default timezone'),
        Parameter('DEFAULT_CONTENT_TYPE', None,
                  'Default content type for this application'),
        Parameter('SITE_MANAGERS', (),
                  'List of email for site managers'),
        Parameter('MD_EXTENSIONS', ['extra', 'meta', 'toc'],
                  'List/tuple of markdown extensions'),
        Parameter('GREEN_POOL', 100,
                  'Run the WSGI handle in a pool of greenlet'),
        Parameter('THREAD_POOL', False,
                  'Run the WSGI handle in the event loop executor'),
        Parameter('SECURE_PROXY_SSL_HEADER', None,
                  'A tuple representing a HTTP header/value combination that '
                  'signifies a request is secure.'),
        #
        # PubSub Channels base parameters
        Parameter('PUBSUB_STORE', None,
                  'Connection string for a Publish/Subscribe data-store'),
        Parameter('PUBSUB_PROTOCOL', 'lux.core.channels.Json',
                  'Encoder and decoder for channel messages. '
                  'Default is json.'),
        Parameter('PUBSUB_PREFIX', None,
                  'Prefix for pubsub channels. If not defined, the APP_NAME'
                  'is used. To skip prefix set to empty string.'),
        #
        Parameter('HTTP_CLIENT_PARAMETERS', None,
                  'A dictionary of parameters to pass to the Http Client')
        ]

    def __init__(self, callable):
        self.callable = callable
        self.meta.argv = callable._argv
        self.meta.script = callable._script
        self.auth_backend = self
        self.threads = threading.local()
        self.providers = {'Http': Http}
        self.models = ModelContainer(self)
        self.extensions = OrderedDict()
        self.config = _build_config(self)
        self.fire('on_config')

    def __call__(self, environ, start_response):
        """The WSGI thing."""
        wsgi_handler = self.wsgi_handler()
        request = self.wsgi_request(environ)
        if self.debug:
            self.logger.debug('Serving request %s' % request.path)
        self.fire('on_request', request)
        return wsgi_handler(environ, start_response)

    def wsgi_handler(self):
        if self._handler is None:
            self.forms = formreg.copy()
            self._handler = _build_handler(self)
            self.fire('on_loaded')
        return self._handler

    @property
    def app(self):
        return self

    @property
    def config_module(self):
        """The :ref:`configuration file <parameters>` used by this
        :class:`.App`.
        """
        return self.meta.module_name

    @property
    def params(self):
        return self.callable._params

    @property
    def _loop(self):
        pool = self.green_pool
        return pool._loop if pool else asyncio.get_event_loop()

    @lazyproperty
    def cache_server(self):
        """Return the Cache handler
        """
        return create_cache(self, self.config['CACHE_SERVER'])

    @lazyproperty
    def green_pool(self):
        if self.config['GREEN_POOL']:
            self.config['THREAD_POOL'] = False
            from pulsar.apps.greenio import GreenPool
            return GreenPool(self.config['GREEN_POOL'])

    def require(self, *extensions):
        return super().require(self, *extensions)

    def has(self, *extensions):
        """Check if this application has a set of ``extensions``
        """
        try:
            self.require(*extensions)
        except ImproperlyConfigured:
            return False
        return True

    def clone_callable(self, **params):
        return self.callable.clone(**params)

    def get_version(self):
        """Get version of this :class:`App`. Required by
        :class:`~.ConsoleParser`."""
        return self.meta.version

    def wsgi_request(self, environ=None, loop=None, path=None,
                     app_handler=None, urlargs=None, **kw):
        """Create a :class:`.WsgiRequest` from a wsgi ``environ`` and set the
        ``app`` attribute in the cache.
        Additional keyed-valued parameters can be inserted.
        """
        if not environ:
            # No WSGI environment, build a test one
            environ = test_wsgi_environ(path=path, loop=loop, **kw)
        request = wsgi_request(environ, app_handler=app_handler,
                               urlargs=urlargs)
        environ['error.handler'] = module_attribute(
            self.config['ERROR_HANDLER'])
        environ['default.content_type'] = self.config['DEFAULT_CONTENT_TYPE']
        # Check if pulsar is serving the application
        if 'pulsar.cfg' not in environ:
            if not self.cfg:
                self.cfg = pulsar.Config(debug=self.debug)
            environ['pulsar.cfg'] = self.cfg
        request.cache.app = self
        request.cache.auth_backend = SimpleBackend()
        return request

    def html_document(self, request):
        """Build the HTML document.

        Usually there is no need to call directly this method.
        Instead one can use the :attr:`.WsgiRequest.html_document`.
        """
        cfg = self.config
        doc = HtmlDocument(title=cfg['HTML_TITLE'],
                           media_path=cfg['MEDIA_URL'],
                           minified=cfg['MINIFIED_MEDIA'],
                           data_debug=self.debug,
                           charset=cfg['ENCODING'],
                           asset_protocol=cfg['ASSET_PROTOCOL'])
        doc.meta = HeadMeta(doc.head)
        doc.jscontext = dict(self._config_context())
        doc.jscontext['lux_version'] = __version__
        # Locale
        lang = cfg['LOCALE'][:2]
        doc.attr('lang', lang)
        #
        # Head
        head = doc.head
        # Add requirejs if url available
        requirejs = cfg['HTML_REQUIREJS_URL']
        if requirejs:
            head.scripts.append(requirejs)

        for script in cfg['HTML_SCRIPTS']:
            head.scripts.append(script)
        #
        for entry in cfg['HTML_META'] or ():
            head.add_meta(**entry)

        self.fire('on_html_document', request, doc, safe=True)
        #
        # Add links last
        links = head.links
        for link in cfg['HTML_LINKS']:
            if isinstance(link, dict):
                links.append(**link)
            else:
                links.append(link)
        return doc

    @lazyproperty
    def commands(self):
        """Load all commands from installed applications"""
        cmnds = OrderedDict()
        available = set()
        for e in reversed(self.config['EXTENSIONS']):
            try:
                modname = e + ('.core' if e == 'lux' else '') + '.commands'
                mod = import_module(modname)
                if hasattr(mod, '__path__'):
                    path = os.path.dirname(getfile(mod))
                    try:
                        commands = []

                        for f in os.listdir(path):
                            if skipfile(f) or not f.endswith('.py'):
                                continue
                            command = f[:-3]
                            if command not in available:
                                available.add(command)
                                commands.append(command)

                        if commands:
                            cmnds[e] = tuple(commands)
                    except OSError:
                        continue
            except ImportError:
                pass    # No management module
        return OrderedDict(((e, cmnds[e]) for e in reversed(cmnds)))

    @lazyproperty
    def email_backend(self):
        """Email backend for this application
        """
        dotted_path = self.config['EMAIL_BACKEND']
        return module_attribute(dotted_path)(self)

    def get_command(self, name):
        """Construct and return a :class:`.Command` for this application
        """
        for e, cmnds in self.commands.items():
            if name in cmnds:
                modname = 'lux.core' if e == 'lux' else e
                mod = import_module('%s.commands.%s' % (modname, name))
                return mod.Command(name, self)
        raise CommandError("Unknown command '%s'" % name)

    def get_usage(self, description=None):
        """Returns the script's main help text, as a string."""
        if not description:
            description = self.config['DESCRIPTION'] or 'Lux toolkit'
        usage = ['',
                 '',
                 '----------------------------------------------',
                 description,
                 '----------------------------------------------',
                 '',
                 "Type '%s <command> --help' for help on a specific command." %
                 (self.meta.script or ''),
                 '', '', "Available commands:", ""]
        for name, commands in self.commands.items():
            usage.append(name)
            usage.extend(('    %s' % cmd for cmd in sorted(commands)))
            usage.append('')
        text = '\n'.join(usage)
        return text

    def get_parser(self, with_commands=True, nargs='?', description=None,
                   **params):
        """Return a python :class:`argparse.ArgumentParser` for parsing
        the command line.

        :param with_commands: Include parsing of all commands (default True).
        :param params: parameters to pass to the
            :class:`argparse.ArgumentParser` constructor.
        """
        if with_commands:
            params['usage'] = self.get_usage(description=description)
            description = None
        parser = super().get_parser(description=description, **params)
        parser.add_argument('command', nargs=nargs, help='command to run')
        return parser

    def on_start(self, server):
        self.fire('on_start', server)

    def load_extension(self, dotted_path):
        """Load an :class:`.LuxExtension` class into this :class:`App`.

        :param dotted_path: python dotted path to the extension.
        :return: an :class:`.LuxExtension` class or ``None``

        If the module contains an :class:`.LuxExtension` class named
        ``LuxExtension``, it will be added to the :attr:`extension` dictionary.
        """
        try:
            module = import_module(dotted_path)
        except ImportError:
            if not self.logger:
                # this is the application extension, raise
                raise
            self.logger.exception('%s cannot load extension %s.',
                                  self, dotted_path)
            return
        Ext = getattr(module, 'Extension', None)
        if Ext and isclass(Ext) and issubclass(Ext, LuxExtension):
            return Ext

    # Template redering
    def template_full_path(self, names):
        """Return a template filesystem full path or None

        Loops through all :attr:`extensions` in reversed order and
        check for ``name`` within the ``templates`` directory
        """
        if not isinstance(names, (list, tuple)):
            names = (names,)
        for name in names:
            for ext in reversed(tuple(self.extensions.values())):
                filename = ext.get_template_full_path(self, name)
                if filename and os.path.exists(filename):
                    return filename
            filename = os.path.join(LUX_CORE, 'templates', name)
            if os.path.exists(filename):
                return filename

    def template(self, name):
        """Load a template from the file system.

        The template is must be located in a ``templates`` directory
        of at least one of the extensions included in the :setting:EXTENSIONS`
        list. The location of the template file is obtained via
        the :meth:`template_full_path` method.

        If the file is not found an empty string is returned.
        """
        if name:
            filename = self.template_full_path(name)
            if filename:
                with open(filename, 'r') as file:
                    return Template(file.read())
        return Template()

    def context(self, request, context=None):
        """Load the ``context`` dictionary for a ``request``.

        This function is called every time a template is rendered via the
        :meth:`render_template` method is used and a the wsgi ``request``
        is passed as key-valued parameter.

        The initial ``context`` is updated with contribution from
        all :setting:`EXTENSIONS` which expose the ``context`` method.
        """
        if (isinstance(context, LuxContext) or
                request.cache._in_application_context):
            return context
        else:
            request.cache._in_application_context = True
            try:
                ctx = LuxContext()
                ctx.update(self.config)
                ctx.update(self.cms.context(request, ctx))
                ctx.update(context or ())
                for ext in self.extensions.values():
                    if hasattr(ext, 'context'):
                        ext.context(request, ctx)
                return ctx
            finally:
                request.cache._in_application_context = False
            return context

    def render_template(self, name, context=None,
                        request=None, engine=None, **kw):
        """Render a template file ``name`` with ``context``
        """
        if request:  # get application context only when request available
            context = self.context(request, context)
        template = self.template(name)
        rnd = self.template_engine(engine)
        return rnd(template, context or (), **kw)

    def template_engine(self, engine=None):
        engine = engine or self.config['DEFAULT_TEMPLATE_ENGINE']
        return template_engine(self, engine)

    def html_response(self, request, page, context=None,
                      jscontext=None, title=None, status_code=None):
        """Html response via a template.

        :param request: the :class:`.WsgiRequest`
        :param page: A :class:`Page`, template file name or a list of
            template filenames
        :param context: optional context dictionary
        """
        request.response.content_type = 'text/html'
        doc = request.html_document
        if jscontext:
            doc.jscontext.update(jscontext)

        if title:
            doc.head.title = title

        if status_code:
            request.response.status_code = status_code
        context = self.context(request, context)
        page = self.cms.as_page(page)
        body = self.cms.render_body(request, page, context)

        doc.body.append(body)

        if not request.config['MINIFIED_MEDIA']:
            doc.head.embedded_js.insert(
                0, 'window.minifiedMedia = false;')

        if doc.jscontext:
            encoded = encode_json(doc.jscontext, self.config['SECRET_KEY'])
            doc.head.add_meta(name="html-context", content=encoded)

        return doc.http_response(request)

    def site_url(self, path=None):
        """Build the site url from an optional ``path``
        """
        base = self.config['SITE_URL']
        path = path or '/'
        if base:
            return base if path == '/' else '%s%s' % (base, path)
        else:
            return path

    def media_url(self, path=None):
        """Build the media url from an optional ``path``
        """
        base = self.config['SITE_URL'] + self.config['MEDIA_URL']
        path = path or '/'
        if base:
            return '%s%s' % (base, path) if path else base
        else:
            return path or '/'

    def add_events(self, event_names):
        """Add additional event names to the event dictionary
        """
        for ext in self.extensions.values():
            self.bind_events(ext, event_names)

    def module_iterator(self, submodule=None, filter=None, cache=None):
        """Iterate over applications modules
        """
        for extension in self.config['EXTENSIONS']:
            try:
                mod = import_module(extension)
            except ImportError:
                # the module is not there
                mod = None
            if mod:
                if submodule:
                    try:
                        mod = import_module('.%s' % submodule, extension)
                    except ImportError:
                        pass
                if filter:
                    yield from _module_types(mod, filter, cache)
                else:
                    yield mod

    @app_attribute
    def http(self):
        """Get an http client for a given key

        A key is used to group together clients so that bandwidths is reduced
        If no key is provided the handler is not included in the http cache.
        """
        return self.providers['Http'](self)

    def run_in_executor(self, callable, *args):
        """Run a ``callable`` in the event loop executor

        It make sure to wait for result if on a green worker

        :param callable: function to execute in the executor
        :param args: parameters
        :return: a future or a synchronous result if on a green worker
        """
        loop = self._loop
        future = loop.run_in_executor(None, callable, *args)
        if self.green_pool and self.green_pool.in_green_worker:
            return self.green_pool.wait(future, True)
        else:
            return future

    async def shell(self, request, command, communicate=None, raw=False):
        """Asynchronous execution of a shell command
        """
        request.logger.info('Execute shell command: %s', command)
        stdin = subprocess.PIPE if communicate else None
        proc = await create_subprocess_shell(command,
                                             stdin=stdin,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
        if communicate:
            msg, err = await proc.communicate(to_bytes(communicate))
        else:
            await proc.wait()
            msg = await proc.stdout.read()
            err = await proc.stderr.read()
        if proc.returncode:
            err = err.decode('utf-8').strip()
            raise ShellError(err, proc.returncode)
        return msg if raw else msg.decode('utf-8').strip()

    def reload(self, *args):
        """Force the reloading of this application

        The reload will occur at the next wsgi request
        """
        if args:
            self.logger.warning('Reload WSGI application')
            self.callable.clear_local()
        else:
            result = self.channels.publish('server', 'reload')
            if result is None:
                self.reload(True)
            else:
                return result

    # INTERNALS
    def _setup_logger(self, config, opts):
        debug = opts.debug or self.params.get('debug', False)
        cfg = pulsar.Config()
        cfg.set('debug', debug)
        cfg.set('log_level', opts.log_level)
        cfg.set('log_handlers', opts.log_handlers)
        self.debug = cfg.debug
        if self.params.get('SETUP_LOGGER', True):
            self.logger = cfg.configured_logger('lux')
        else:
            super()._setup_logger(config, opts)

    def _config_context(self):
        cfg = self.config
        return ((p.name, cfg[p.name]) for p in cfg['_parameters'].values()
                if p.jscontext)


# INTERNALS
def _add_app(apps, name, pos=None):
    try:
        apps.remove(name)
    except ValueError:
        pass
    if pos is not None:
        apps.insert(pos, name)
    else:
        apps.append(name)


def _module_types(mod, filter, cache=None):
    # Loop through attributes in mod_models
    if cache and hasattr(mod, cache):
        for value in getattr(mod, cache):
            yield value
    else:
        all = []
        if cache:
            setattr(mod, cache, all)
        for name in dir(mod):
            value = getattr(mod, name)
            if filter(value):
                all.append(value)
                yield value


def _build_config(self):
    module_name = self.callable._config_file or 'lux'
    module = import_module(module_name)
    self.meta = self.meta.copy(module)
    if self.meta.name != 'lux':
        extension = self.load_extension(self.meta.name)
        if extension:   # extension available, get the version from it
            self.meta.version = extension.meta.version
    #
    parser = self.get_parser(with_commands=False, add_help=False)
    opts, _ = parser.parse_known_args(self.meta.argv)
    config_module = import_module(opts.config)

    if opts.config != self.config_module:
        raise ConfigError(opts.config)
    #
    # setup application
    config = {'_parameters': {}}
    self.setup(config, opts)
    configs = _load_configs(self, config, config_module)
    #
    # Load extensions
    self.logger.debug('Setting up extensions')
    apps = list(config['EXTENSIONS'])
    _add_app(apps, 'lux', 0)
    if self.meta.name != 'lux':
        _add_app(apps, self.meta.name)

    extensions = self.extensions
    for name in apps[1:]:
        Ext = self.load_extension(name)
        if Ext:
            extension = Ext()
            extensions[extension.meta.name] = extension
            self.bind_events(extension)
            extension.setup(config)

    params = configs.pop()
    _config_from_json(configs, config)
    config.update(params)
    config['EXTENSIONS'] = tuple(apps)
    return config


def _build_handler(self):
    engine = self.template_engine('python')
    parameters = self.config.pop('_parameters')
    self.config = render_data(self, self.config, engine, self.config)
    self.config['_parameters'] = parameters
    self.channels = Channels(self)

    if not self.cms:
        self.cms = CMS(self)

    extensions = list(self.extensions.values())
    middleware, rmiddleware = _build_middleware(self, extensions, [], [])
    # Response middleware executed in reversed order
    rmiddleware = list(reversed(rmiddleware))
    #
    # Use a green pool
    if self.green_pool:
        middleware.insert(0, self.channels.green_middleware)
        handler = GreenWSGI(middleware, self.green_pool, rmiddleware)
    #
    # Use thread pool
    elif self.config['THREAD_POOL']:
        hnd = WsgiHandler(middleware, rmiddleware, async=False)
        handler = WsgiHandler([wait_for_body_middleware,
                               middleware_in_executor(hnd)])
    #
    else:
        raise ImproperlyConfigured(
            'Green or thread concurrency required. Please specify '
            'either GREEN_POOL or THREAD_POOL size')

    return handler


def _build_middleware(self, extensions, middleware, rmiddleware):
    for extension in extensions:
        middle = extension.middleware(self)
        if middle:
            middleware.extend(middle)
        middle = extension.response_middleware(self)
        if middle:
            rmiddleware.extend(middle)

    return middleware, rmiddleware


def _load_configs(self, config, config_module):
    params = self.params.copy()
    cfg = dict(_load_config(vars(config_module)))
    configs = [cfg]
    settings_files = multi_pop('SETTINGS_FILES', cfg, params)

    if settings_files:
        if isinstance(settings_files, str):
            settings_files = [settings_files]
        ok = []

        for filename in settings_files:
            try:
                with open(filename) as fp:
                    cfg = json.load(fp)
            except FileNotFoundError:
                self.logger.error('Could not load "%s", no such file',
                                  filename)
            except json.JSONDecodeError:
                self.logger.error('Could not json decode "%s", skipping',
                                  filename)
            else:
                cfg.pop('SETTINGS_FILES', None)
                configs.append(cfg)
                ok.append(filename)

        if ok:
            config['SETTINGS_FILES'] = ok

    configs.append(params)
    config['EXTENSIONS'] = multi_pop('EXTENSIONS', *configs) or ()
    return configs


def _load_config(cfg):
    for name, value in cfg.items():
        if name == name.upper():
            yield name, value


def _config_from_json(configs, parameters):

    for config in configs:
        extend_config(parameters, config)
