"""Lux Application class
"""
import os
import asyncio
import logging
from asyncio import create_subprocess_shell, subprocess, new_event_loop

from inspect import isclass
from collections import OrderedDict
from importlib import import_module

from pulsar.api import ImproperlyConfigured, Config, EventHandler, context
from pulsar.utils.log import lazyproperty
from pulsar.utils.importer import module_attribute
from pulsar.apps.greenio import GreenHttp
from pulsar.apps.http import HttpClient
from pulsar.apps.test import test_wsgi_request
from pulsar.utils.string import to_bytes
from pulsar.utils.slugify import slugify

from lux import __version__

from .commands import ConfigError, ConsoleMixin
from .extension import LuxExtension, Parameter, ALL_EVENTS
from .wrappers import ERROR_MESSAGES
from .templates import render_data, template_engine, Template
from .cms import CMS
from .cache import create_cache
from .exceptions import ShellError
from .channels import LuxChannels
from .green import Handler
from .routers import Router, raise404

from ..models import ModelContainer
from ..utils.context import app_attribute, set_app, set_request


LUX_CORE = os.path.dirname(__file__)
LOCAL_LOGGER = logging.getLogger('lux.api.local')


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


def Http(app):
    params = app.config['HTTP_CLIENT_PARAMETERS'] or {}
    green = app.green_pool
    if not green:
        params['loop'] = new_event_loop()
    http = HttpClient(**params)
    return GreenHttp(http) if green else http


def is_html(app):
    return app.config['DEFAULT_CONTENT_TYPE'] == 'text/html'


class Application(ConsoleMixin, LuxExtension, EventHandler):
    """A WSGI callable for serving lux applications.
    """
    channels = None
    debug = False
    logger = None
    _handler = None
    cms = None
    """CMS handler"""
    api = None
    _http = None
    _config = [
        #
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
        Parameter('ERROR_HANDLER', 'lux.core.exceptions:error_handler',
                  'Dotted path to handler of Http exceptions'),
        Parameter('ERROR_MESSAGES', None,
                  'Override default rror messages'),
        Parameter('MEDIA_URL', '/media/',
                  'the base url for static files', True),
        Parameter('MINIFIED_MEDIA', True,
                  'Use minified media files. All media files will replace '
                  'their extensions with .min.ext. For example, javascript '
                  'links *.js become *.min.js', True),
        #
        Parameter('SERVER_NAME', 'Lux/%s' % __version__),
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
        Parameter('HTML_BODY_SCRIPTS', [],
                  'List of scripts to include at the end of the body tag'),
        Parameter('HTML_META',
                  [{'http-equiv': 'X-UA-Compatible',
                    'content': 'IE=edge'},
                   {'name': 'viewport',
                    'content': 'width=device-width, initial-scale=1'}],
                  'List of default ``meta`` elements to add to the html head'
                  'element'),
        Parameter('HTML_FORM_TAG', 'lux-form',
                  'Html tag for lux forms'),
        Parameter('HTML_GRID_TAG', 'lux-grid',
                  'Html tag for lux grids'),
        #
        # CONTENT base parameters
        Parameter('CONTENT_LINKS',
                  {'python': 'https://www.python.org/',
                   'lux': 'https://github.com/quantmind/lux',
                   'pulsar': 'http://pythonhosted.org/pulsar'},
                  'Links used throughout the web site'),
        #
        # BASE email parameters
        Parameter('EMAIL_BACKEND', 'lux.core.mail:EmailBackend',
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
        #
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
        Parameter('CHANNEL_SERVER', 'server',
                  'Channel name for the server'),
        #
        Parameter('HTTP_CLIENT_PARAMETERS', None,
                  'A dictionary of parameters to pass to the Http Client'),
        #
        # Authentication
        Parameter('AUTHENTICATION_BACKEND', 'lux.core.auth:AuthBackend',
                  'Dotted path to a classe which provides '
                  'a backend for authentication.'),
        Parameter('JWT_ALGORITHM', 'HS512', 'Signing algorithm')
        ]

    def __init__(self, callable):
        self.callable = callable
        self.cfg = callable.cfg
        self.meta.argv = callable.argv
        self.meta.script = callable.script
        self.cache = {}
        self.providers = {
            'Http': Http,
            'Channels': LuxChannels.create
        }
        self.models = ModelContainer().init_app(self)
        self.extensions = OrderedDict()
        self.config = _build_config(self)
        self.event('on_config').fire()
        cfg = self.config
        self.auth = module_attribute(cfg['AUTHENTICATION_BACKEND'])(self)
        self.cache_server = create_cache(self, cfg['CACHE_SERVER'])
        self.on_error = module_attribute(cfg['ERROR_HANDLER'])

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
        return self.callable.params

    @property
    def argv(self):
        return self.callable.argv

    @property
    def description(self):
        return self.callable.description

    @property
    def _loop(self):
        pool = self.green_pool
        return pool._loop if pool else asyncio.get_event_loop()

    @lazyproperty
    def green_pool(self):
        if self.config['GREEN_POOL']:
            self.config['THREAD_POOL'] = False
            from pulsar.apps.greenio import GreenPool
            return GreenPool(self.config['GREEN_POOL'])

    def __call__(self, environ, start_response):
        """The WSGI thing."""
        return self.request_handler()(environ, start_response)

    def request_handler(self):
        if not self._handler:
            context.setup()
            set_app(self)
            self._handler = _build_handler(self)
            self.event('on_loaded').fire()
        return self._handler

    def wsgi_request(self, **kw):
        """Used for testing"""
        request = self.green_pool.wait(test_wsgi_request(**kw))
        self.on_request(request)
        return request

    def on_request(self, data=None):
        request = data
        config = self.config
        environ = request.environ
        environ['error.handler'] = self.on_error
        environ['default.content_type'] = config['DEFAULT_CONTENT_TYPE']
        cache = request.cache
        cache.app = self
        # set request and app in the asyncio task context
        set_request(request)
        self.auth.on_request(request)
        self.fire_event('on_request', data=request)

    def form_data(self, request):
        data, files = request.data_and_files()
        self.fire_event('on_form', data=(request, data, files))
        return data, files

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

    def close(self):
        self.green_pool.shutdown(False)
        self.fire('on_close')

    @lazyproperty
    def email_backend(self):
        """Email backend for this application
        """
        dotted_path = self.config['EMAIL_BACKEND']
        return module_attribute(dotted_path)(self)

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

    async def shell(self, request, command, communicate=None,
                    raw=False, chdir=None):
        """Asynchronous execution of a shell command
        """
        if chdir:
            command = 'cd %s && %s' % (chdir, command)
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
        elif self.channels is not None:
            return self.channels.publish(
                self.config['CHANNEL_SERVER'], 'reload'
            )
        else:
            self.reload(True)

    def bind_extension_events(self, extension, events=None):
        '''Bind ``events`` from an ``extension``.

        :param extension: an class:`.Extension`
        :param events: optional list of event names. If not supplied,
            the default lux events are used.
        '''
        events = events or ALL_EVENTS
        for name in events:
            handler = getattr(extension, name, None)
            if handler:
                self.event(name).bind(handler)

    # INTERNALS
    def _setup_logger(self, config, opts):
        debug = opts.debug or self.params.get('debug', False)
        cfg = Config()
        cfg.set('debug', debug)
        cfg.set('log_level', opts.log_level)
        cfg.set('log_handlers', opts.log_handlers)
        self.debug = cfg.debug
        if self.params.get('SETUP_LOGGER', True):
            self.logger = cfg.configured_logger('lux')
        else:
            super()._setup_logger(config, opts)


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
    module_name = self.callable.config_file or 'lux'
    module = import_module(module_name)
    self.meta = self.meta.copy(module)
    if self.meta.name != 'lux':
        extension = _load_extension(self.meta.name)
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
    cfg = dict(_load_config(vars(config_module)))
    prefix = slugify(cfg.get('APP_NAME', ''), '_').upper()
    config = {'_parameters': {}}
    #
    # Load extensions
    self.setup(config, cfg, prefix, opts=opts)
    self.logger.debug('Setting up extensions')
    apps = list(config['EXTENSIONS'])
    _add_app(apps, 'lux', 0)
    if self.meta.name != 'lux':
        _add_app(apps, self.meta.name)

    extensions = self.extensions
    for name in apps[1:]:
        Ext = _load_extension(name)
        if Ext:
            extension = Ext()
            extensions[extension.meta.name] = extension
            self.bind_extension_events(extension)
            extension.setup(config, cfg, prefix)

    config.update(((k, v) for k, v in self.params.items() if k == k.upper()))
    config['EXTENSIONS'] = tuple(apps)
    error_messages = ERROR_MESSAGES.copy()
    error_messages.update(config.get('ERROR_MESSAGES') or ())
    config['ERROR_MESSAGES'] = error_messages
    return config


def _build_handler(self):
    engine = self.template_engine('python')
    parameters = self.config.pop('_parameters')
    self.config = render_data(self, self.config, engine, self.config)
    self.config['_parameters'] = parameters
    self.channels = self.providers['Channels'](self)

    if not self.cms:
        self.cms = CMS()
    self.cms.init_app(self)

    extensions = list(self.extensions.values())
    all_routes = []
    responses = []
    root = None
    for extension in extensions:
        handler = getattr(extension, 'on_response', None)
        if handler:
            responses.append(handler)
        for route in (extension.routes(self) or ()):
            if route.full_route.match('') is not None:
                if root:
                    raise ImproperlyConfigured(
                        "Root route already available, cannot add another from"
                        " %s extension" % extension
                    )
                root = route
            else:
                all_routes.append(route)

    all_routes.extend(self.cms.middleware())

    if not root:
        root = Router('/', get=raise404)

    for route in all_routes:
        root.add_route(route)

    if responses:
        event = self.event('on_response')
        for handler in reversed(responses):
            event.bind(handler)
    #
    return Handler(self, root)


def _load_config(cfg):
    for name, value in cfg.items():
        if name == name.upper():
            yield name, value


def _load_extension(dotted_path):
    module = import_module(dotted_path)
    Ext = getattr(module, 'Extension', None)
    if Ext and isclass(Ext) and issubclass(Ext, LuxExtension):
        return Ext
