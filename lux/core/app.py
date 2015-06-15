import sys
import os
import json
from inspect import isclass, getfile
from collections import OrderedDict
from importlib import import_module

import pulsar
from pulsar import ImproperlyConfigured
from pulsar.utils.httpurl import remove_double_slash
from pulsar.apps.wsgi import (WsgiHandler, HtmlDocument, test_wsgi_environ,
                              LazyWsgi, wait_for_body_middleware,
                              middleware_in_executor)
from pulsar.utils.log import lazyproperty
from pulsar.utils.importer import module_attribute

from .commands import ConsoleParser, CommandError
from .extension import Extension, Parameter, EventMixin
from .wrappers import wsgi_request, HeadMeta, error_handler
from .engines import template_engine
from .cms import CMS
from .cache import create_cache


__all__ = ['App',
           'Application',
           'execute_from_config']


LUX_CORE = os.path.dirname(__file__)


def execute_from_config(config_file, **params):     # pragma    nocover
    '''Create and run an :class:`.Application` from a ``config_file``.

    This is the function to use when creating the script which runs your
    web applications::

        import lux

        if __name__ == '__main__':
            lux.execute_from_config('path.to.config')

    :param config_file: the python dotted path to the config file for setting
        up a new :class:`App`. The config file should be located in the
        python module which implements the main application
        of the web site.
    '''
    return execute_app(App(config_file, **params))


def execute_app(app, argv=None, **params):  # pragma    nocover
    '''Execute a given ``app``.

    :parameter app: the :class:`.App` to execute
    :parameter argv: optional list of parameters, if not given ``sys.argv``
        is used instead.
    :parameter params: additional key-valued parameters to pass to the
        :class:`.Command` executing the ``app``.
    '''
    if argv is None:
        argv = app._argv or sys.argv
    app._argv = argv = list(argv)
    if argv:
        app._script = argv.pop(0)
    try:
        application = app.commands()
    except ImproperlyConfigured as e:
        print('IMPROPERLY CONFUGURED: %s' % e)
        exit(1)
    # Parse for the command
    parser = application.get_parser(add_help=False)
    opts, _ = parser.parse_known_args(argv)
    #
    # we have a command
    if opts.command:
        try:
            command = application.get_command(opts.command)
        except CommandError as e:
            print('\n'.join(('%s.' % e, 'Pass -h for list of commands')))
            exit(1)
        # Make sure the loop exists
        argv = list(argv)
        argv.remove(command.name)
        try:
            return command(argv, **params)
        except CommandError as e:
            print(str(e))
            exit(1)
    else:
        # this should fail unless we pass -h
        parser = application.get_parser(nargs=1)
        parser.parse_args(argv)


class App(LazyWsgi):

    def __init__(self, config_file, script=None, argv=None, **params):
        self._params = params
        self._config_file = config_file
        self._script = script
        self._argv = argv

    def setup(self, environ=None):
        return Application(self)

    def commands(self):
        return Application(self, handler=False)


class Application(ConsoleParser, Extension, EventMixin):
    '''The :class:`.Application` is the WSGI callable for serving
    lux applications.

    It is a specialised :class:`~.Extension` which collects
    all extensions of your application and setup the wsgi middleware used by
    the web server.
    An :class:`App` is not usually initialised directly, the higher level
    :func:`.execute_from_config` is used instead.

    .. attribute:: config

        The configuration dictionary containing all patameters specified in
        the :attr:`config_module`.

    .. attribute:: debug

        debug flag set at runtime via the ``debug`` flag::

            python myappscript.py serve --debug

    .. attribute:: handler

        The :class:`~pulsar.apps.wsgi.handlers.WsgiHandler` for this
        application. It is created the first time the callable
        method of this :class:`.Application` is accessed by the WSGI
        server.

    .. attribute:: auth_backend

        Used by the sessions extension

    '''
    cfg = None
    debug = False
    logger = None
    admin = None
    handler = None
    auth_backend = None
    thread_pool = True
    _worker = None
    _WsgiHandler = WsgiHandler
    _config = [
        Parameter('EXTENSIONS', [],
                  'List of extension names to use in your application. '
                  'The order matter since the wsgi middleware of extension is '
                  'processed in the order given by this setting.'),
        Parameter('DESCRIPTION', None,
                  'A description to display before the argument help on the '
                  'command line when running commands'),
        Parameter('ENCODING', 'utf-8',
                  'Default encoding for text.'),
        Parameter('ERROR_HANDLER', error_handler,
                  'Handler of Http exceptions'),
        Parameter('HTML_TITLE', 'Lux',
                  'Default HTML Title'),
        Parameter('MEDIA_URL', '/media/',
                  'the base url for static files', True),
        Parameter('MINIFIED_MEDIA', True,
                  'Use minified media files. All media files will replace '
                  'their extensions with .min.ext. For example, javascript '
                  'links *.js become *.min.js', True),
        Parameter('HTML_LINKS', [],
                  'List of links to include in the html head tag.'),
        Parameter('SCRIPTS', [],
                  'List of scripts to load in the head tag'),
        Parameter('COPYRIGHT', 'Lux',
                  'Site Copyright', True),
        Parameter('REQUIREJS_URL',
                  "//cdnjs.cloudflare.com/ajax/libs/require.js/2.1.18/require",
                  'Default url for requirejs. Set to None if no requirejs '
                  'is needed by your application'),
        Parameter('REQUIREJS', (),
                  'Default Required javascript. Loaded via requirejs.'),
        Parameter('ASSET_PROTOCOL', '',
                  ('Default protocol for scripts and links '
                   '(could be http: or https:)')),
        Parameter('HTML_META',
                  [{'http-equiv': 'X-UA-Compatible',
                    'content': 'IE=edge'},
                   {'name': 'viewport',
                    'content': 'width=device-width, initial-scale=1'}],
                  'List of default ``meta`` elements to add to the html head'
                  'element'),
        Parameter('DATE_FORMAT', 'd MMM y',
                  'Default formatting for dates in JavaScript', True),
        Parameter('DATETIME_FORMAT', 'd MMM y, h:mm:ss a',
                  'Default formatting for dates in JavaScript', True),
        Parameter('DEFAULT_TEMPLATE_ENGINE', 'python',
                  'Default template engine'),
        Parameter('APP_NAME', 'Lux', 'Application site name', True),
        Parameter('SITE_URL', None,
                  'Web site url'),
        Parameter('LINKS',
                  {'python': 'https://www.python.org/',
                   'lux': 'https://github.com/quantmind/lux',
                   'pulsar': 'http://pythonhosted.org/pulsar'},
                  'Links used throughout the web site'),
        Parameter('CACHE_SERVER', 'dummy://',
                  ('Cache server, can be a connection string to a valid '
                   'datastore which support the cache protocol or an object '
                   'supporting the cache protocol')),
        Parameter('DEFAULT_FROM_EMAIL', '',
                  'Default email address to send email from'),
        Parameter('LOCALE', 'en_GB', 'Default locale', True),
        Parameter('DEFAULT_TIMEZONE', 'GMT',
                  'Default timezone'),
        Parameter('DEFAULT_CONTENT_TYPE', None,
                  'Default content type for this application'),
        Parameter('HTML_TEMPLATES', {'/': 'home.html'},
                  'Dictionary of Html templates to render'),
        Parameter('SITE_MANAGERS', (),
                  'List of email for site managers'),
        Parameter('EMAIL_BACKEND', 'lux.core.mail.EmailBackend',
                  'Default locale'),
        Parameter('MD_EXTENSIONS', ['extra', 'meta', 'toc'],
                  'List/tuple of markdown extensions'),
        Parameter('GREEN_POOL', 0,
                  'Run the WSGI handle in a pool of greenlet'),
        Parameter('SECURE_PROXY_SSL_HEADER', None,
                  'A tuple representing a HTTP header/value combination that '
                  'signifies a request is secure.')
        ]

    def __init__(self, callable, handler=True):
        self.callable = callable
        self.meta.argv = callable._argv
        self.meta.script = callable._script
        self.config = self._build_config(callable._config_file)
        self.fire('on_config')
        if handler:
            self.get_handler()

    def __call__(self, environ, start_response):
        '''The WSGI thing.'''
        request = self.wsgi_request(environ)
        if self.debug:
            self.logger.debug('Serving request %s' % request.path)
        self.fire('on_request', request)
        return self.handler(environ, start_response)

    @property
    def config_module(self):
        '''The :ref:`configuration file <parameters>` used by this
        :class:`.App`.
        '''
        return self.meta.module_name

    @property
    def extensions(self):
        '''Ordered dictionary of :class:`.Extension` available.

        The order is the same as in the
        :setting:`EXTENSIONS` config parameter.
        '''
        return self.config['EXTENSION_HANDLERS']

    @property
    def params(self):
        return self.callable._params

    @property
    def _loop(self):
        if self._worker:
            return self._worker._loop

    @lazyproperty
    def cache_server(self):
        '''Return the Cache handler
        '''
        return create_cache(self, self.config['CACHE_SERVER'])

    @lazyproperty
    def green_pool(self):
        if self.config['GREEN_POOL']:
            from pulsar.apps.greenio import GreenPool
            return GreenPool(self.config['GREEN_POOL'])

    def get_handler(self):
        if self.handler is None:
            self._worker = pulsar.get_actor()
            self.cms = CMS(self)
            self.handler = self._build_handler()
            self.fire('on_loaded')
            wsgi = None
            if self.green_pool:
                self.logger.info('Setup green Wsgi handler')
                wsgi = WsgiGreen(self.handler, self.green_pool)
            elif self.thread_pool:
                wsgi = middleware_in_executor(self.handler)

            if wsgi:
                self.handler = WsgiHandler((wait_for_body_middleware, wsgi),
                                           async=True)
        return self.handler

    def get_version(self):
        '''Get version of this :class:`App`. Required by
        :class:`.ConsoleParser`.'''
        return self.meta.version

    def wsgi_request(self, environ=None, loop=None, path=None,
                     app_handler=None, urlargs=None, **kw):
        '''Create a :class:`.WsgiRequest` from a wsgi ``environ`` and set the
        ``app`` attribute in the cache.
        Additional keyed-valued parameters can be inserted.
        '''
        if not environ:
            # No WSGI environment, build a test one
            environ = test_wsgi_environ(path=path, loop=loop, **kw)
        request = wsgi_request(environ, app_handler=app_handler,
                               urlargs=urlargs)
        environ['error.handler'] = self.config['ERROR_HANDLER']
        environ['default.content_type'] = self.config['DEFAULT_CONTENT_TYPE']
        # Check if pulsar is serving the application
        if 'pulsar.cfg' not in environ:
            if not self.cfg:
                self.cfg = pulsar.Config(debug=self.debug)
            environ['pulsar.cfg'] = self.cfg

        request.cache.app = self
        return request

    def html_document(self, request):
        '''Build the HTML document.

        Usually there is no need to call directly this method.
        Instead one can use the :attr:`.WsgiRequest.html_document`.
        '''
        cfg = self.config
        site_url = cfg['SITE_URL']
        media_path = cfg['MEDIA_URL']
        if site_url:
            media_path = site_url + media_path
        doc = HtmlDocument(title=cfg['HTML_TITLE'],
                           media_path=media_path,
                           minified=cfg['MINIFIED_MEDIA'],
                           data_debug=self.debug,
                           charset=cfg['ENCODING'],
                           asset_protocol=cfg['ASSET_PROTOCOL'])
        doc.meta = HeadMeta(doc.head)
        doc.jscontext = dict(((p.name, cfg[p.name])
                              for p in cfg['_parameters'].values()
                              if p.jscontext))
        # Locale
        lang = cfg['LOCALE'][:2]
        doc.attr('lang', lang)
        #
        # Head
        head = doc.head
        # Add requirejs if url available
        requirejs = cfg['REQUIREJS_URL']
        if requirejs:
            head.scripts.append(requirejs)

        for script in cfg['SCRIPTS']:
            head.scripts.append(script)
        #
        for entry in cfg['HTML_META'] or ():
            head.add_meta(**entry)

        self.fire('on_html_document', request, doc)
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
        '''Load all commands from installed applications'''
        cmnds = OrderedDict()
        for e in self.config['EXTENSIONS']:
            try:
                modname = e + ('.core' if e == 'lux' else '') + '.commands'
                mod = import_module(modname)
                if hasattr(mod, '__path__'):
                    path = os.path.dirname(getfile(mod))
                    try:
                        commands = tuple((f[:-3] for f in os.listdir(path)
                                          if not f.startswith('_') and
                                          f.endswith('.py')))
                        if commands:
                            cmnds[e] = commands
                    except OSError:
                        continue
            except ImportError:
                pass    # No management module
        return cmnds

    @lazyproperty
    def email_backend(self):
        '''Email backend for this application
        '''
        dotted_path = self.config['EMAIL_BACKEND']
        return module_attribute(dotted_path)(self)

    def get_command(self, name):
        '''Construct and return a :class:`.Command` for this application
        '''
        for e, cmnds in self.commands.items():
            for cmnd in cmnds:
                if name == cmnd:
                    modname = 'lux.core' if e == 'lux' else e
                    mod = import_module('%s.commands.%s' % (modname, name))
                    return mod.Command(name, self)
        raise CommandError("Unknown command '%s'" % name)

    def get_usage(self):
        '''Returns the script's main help text, as a string.'''
        description = self.config['DESCRIPTION'] or 'Lux toolkit'
        usage = ['', '', description, '',
                 "Type '%s <command> --help' for help on a specific command." %
                 (self.meta.script or ''),
                 '', '', "Available commands:", ""]
        for name, commands in self.commands.items():
            usage.append(name)
            usage.extend(('    %s' % cmd for cmd in sorted(commands)))
            usage.append('')
        text = '\n'.join(usage)
        return text

    def get_parser(self, with_commands=True, nargs='?', **params):
        '''Return a python :class:`argparse.ArgumentParser` for parsing
        the command line.

        :param with_commands: Include parsing of all commands (default True).
        :param params: parameters to pass to the
            :class:`argparse.ArgumentParser` constructor.
        '''
        if with_commands:
            params['usage'] = self.get_usage()
        parser = super().get_parser(**params)
        parser.add_argument('command', nargs=nargs, help='command to run')
        return parser

    def on_start(self, server):
        self.fire('on_start', server)

    def load_extension(self, dotted_path):
        '''Load an :class:`.Extension` class into this :class:`App`.

        :param dotted_path: python dotted path to the extension.
        :return: an :class:`.Extension` class or ``None``

        If the module contains an :class:`.Extension` class named
        ``Extension``, it will be added to the :attr:`extension` dictionary.
        '''
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
        if Ext and isclass(Ext) and issubclass(Ext, Extension):
            return Ext

    # Template redering
    def template_full_path(self, names):
        '''Return the template full path or None.

        Loops through all :attr:`extensions` in reversed order and
        check for ``name`` within the ``templates`` directory
        '''
        if not isinstance(names, (list, tuple)):
            names = (names,)
        for name in names:
            for ext in reversed(tuple(self.extensions.values())):
                filename = os.path.join(ext.meta.path, 'templates', name)
                if os.path.exists(filename):
                    return filename
            filename = os.path.join(LUX_CORE, 'templates', name)
            if os.path.exists(filename):
                return filename
        self.logger.error('Template %s not found' % name)

    def template(self, name):
        '''Load a template from the file system.

        The template is must be located in a ``templates`` directory
        of at least one of the extensions included in the :setting:EXTENSIONS`
        list. The location of the template file is obtained via
        the :meth:`template_full_path` method.

        If the file is not found an empty string is returned.
        '''
        filename = self.template_full_path(name)
        if filename:
            with open(filename, 'r') as file:
                return file.read()
        return ''

    def context(self, request, context=None):
        '''Load the ``context`` dictionary for a ``request``.

        This function is called every time a template is rendered via the
        :meth:`render_template` method is used and a the wsgi ``request``
        is passed as key-valued parameter.

        The initial ``context`` is updated with contribution from
        all :setting:`EXTENSIONS` which expose the ``context`` method.
        '''
        context = context if context is not None else {}
        context.update(request.app.config)
        for ext in self.extensions.values():
            if hasattr(ext, 'context'):
                context = ext.context(request, context) or context
        return context

    def render_template(self, name, context=None, request=None, engine=None):
        '''Render a template file ``name`` with ``context``
        '''
        if request:
            context = self.context(request, context)
        template = self.template(name)
        rnd = self.template_engine(engine)
        return rnd(template, context)

    def template_engine(self, engine=None):
        engine = engine or self.config['DEFAULT_TEMPLATE_ENGINE']
        return template_engine(engine)

    def html_response(self, request, template_name, context=None,
                      jscontext=None, title=None, status_code=None):
        '''Html response via a template.

        :param request: the :class:`.WsgiRequest`
        :param template_name: the template file name to load
        :param context: optional context dictionary
        '''
        if 'text/html' in request.content_types:
            request.response.content_type = 'text/html'
            doc = request.html_document
            if jscontext:
                doc.jscontext.update(jscontext)
            head = doc.head
            if title:
                head.title = title % head.title
            if status_code:
                request.response.status_code = status_code
            context = self.context(request, context)
            if doc.jscontext:
                jscontext = json.dumps(doc.jscontext)
                doc.head.embedded_js.insert(
                    0, 'var lux = {context: %s};\n' % jscontext)
            body = self.render_template(template_name, context)
            doc.body.append(body)
            return doc.http_response(request)

    def site_url(self, path=None):
        '''Build the site url from an optional ``path``
        '''
        base = self.config['SITE_URL']
        path = path or '/'
        if base:
            return base if path == '/' else '%s%s' % (base, path)
        else:
            return path

    def media_url(self, path=None):
        '''Build the media url from an optional ``path``
        '''
        base = self.config['SITE_URL'] + self.config['MEDIA_URL']
        path = path or '/'
        if base:
            return '%s%s' % (base, path) if path else base
        else:
            return path or '/'

    def require(self, *extensions):
        for ext in extensions:
            if ext not in self.config['EXTENSIONS']:
                raise ImproperlyConfigured('Requires "%s" extension' % ext)

    def add_events(self, event_names):
        '''Add additional event names to the event dictionary
        '''
        for ext in self.extensions.values():
            self.bind_events(ext, event_names)

    def module_iterator(self, submodule=None, filter=None, cache=None):
        '''Iterate over applications modules
        '''
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
                    yield from module_types(mod, filter, cache)
                else:
                    yield mod

    # INTERNALS
    def _build_config(self, module_name):
        # Check if an extension module is available
        module = import_module(module_name)
        self.meta = self.meta.copy(module)
        if self.meta.name != 'lux':
            # self.meta.path.add2python(self.meta.name, up=1)
            extension = self.load_extension(self.meta.name)
            if extension:   # extension available, get the version from it
                self.meta.version = extension.meta.version
        #
        parser = self.get_parser(with_commands=False, add_help=False)
        opts, _ = parser.parse_known_args(self.meta.argv)
        config_module = import_module(opts.config)
        if opts.config != self.config_module:
            # Different config file, configure again
            return self._build_config(config_module.__file__)
        #
        # setup application
        config = {}
        self.setup(config, config_module, self.params, opts)
        #
        # Load extensions
        self.logger.debug('Setting up extensions')
        apps = list(config['EXTENSIONS'])
        add_app(apps, 'lux', 0)
        add_app(apps, self.meta.name)
        media_url = config['MEDIA_URL']
        if media_url:
            config['MEDIA_URL'] = remove_double_slash('/%s/' % media_url)
        config['EXTENSIONS'] = tuple(apps)
        config['EXTENSION_HANDLERS'] = extensions = OrderedDict()
        for name in config['EXTENSIONS'][1:]:
            Ext = self.load_extension(name)
            if Ext:
                extension = Ext()
                extensions[extension.meta.name] = extension
                self.bind_events(extension)
                extension.setup(config, config_module, self.params)
        return config

    def _build_handler(self):
        '''The WSGI application handler for this :class:`App`.

        It is lazily loaded the first time it is accessed so that
        this :class:`App` can be used by pulsar in a multiprocessing setup.
        '''
        # do this here so that the config is already loaded before fire signal
        extensions = list(self.extensions.values())
        middleware = []
        rmiddleware = []
        for extension in extensions:
            _middleware = extension.middleware(self)
            if _middleware:
                middleware.extend(_middleware)
            _middleware = extension.response_middleware(self)
            if _middleware:
                rmiddleware.extend(_middleware)
        # Response middleware executed in reversed order
        rmiddleware = list(reversed(rmiddleware))
        return self._WsgiHandler(middleware, response_middleware=rmiddleware)

    def _setup_logger(self, config, module, opts):
        debug = opts.debug or self.params.get('debug', False)
        cfg = pulsar.Config()
        cfg.set('debug', debug)
        cfg.set('loglevel', opts.loglevel)
        cfg.set('loghandlers', opts.loghandlers)
        self.debug = cfg.debug
        self.logger = cfg.configured_logger('lux')


class WsgiGreen:
    '''Wraps a Wsgi application to be executed on a pool of greenlet
    '''
    def __init__(self, wsgi, pool):
        from pulsar.apps.greenio import wait
        self.wsgi = wsgi
        self.pool = pool
        self.wait = wait

    def __call__(self, environ, start_response):
        return self.pool.submit(self._green_handler, environ, start_response)

    def _green_handler(self, environ, start_response):
        # Running on a greenlet worker
        return self.wait(self.wsgi(environ, start_response))


def add_app(apps, name, pos=None):
    try:
        apps.remove(name)
    except ValueError:
        pass
    if pos is not None:
        apps.insert(pos, name)
    else:
        apps.append(name)


def module_types(mod, filter, cache=None):
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
