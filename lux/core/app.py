'''
High level Functions
=====================

.. autofunction:: execute_from_config


.. autofunction:: execute_app


Application
=====================

.. autoclass:: App
   :members:
   :member-order: bysource

'''
import sys
import os
import logging
import pickle
import json
from inspect import isclass
from collections import OrderedDict
from importlib import import_module

from pulsar.utils.httpurl import remove_double_slash
from pulsar.apps.wsgi import WsgiHandler, HtmlDocument, test_wsgi_environ
from pulsar.utils.pep import itervalues
from pulsar.utils.log import LocalMixin, local_property, local_method

from .commands import ConsoleParser, CommandError
from .extension import Extension, Parameter
from .wrappers import WsgiRequest, JsonDocument
from .engines import template_engine


__all__ = ['App',
           'execute_from_config',
           'execute_from_command_line']


# All events are fired with app as first positional argument
ALL_EVENTS = ('on_config',  # Config ready.
              'on_loaded',  # Wsgi handler ready. Extra args: handler
              'on_start',  # Wsgi server starts. Extra args: server
              'on_request',  # Fired when a new request arrives
              'on_html_document',  # Html doc built. Extra args: request, html
              'on_form',  # Form constructed. Extra args: form
              'on_html_response'  # Response is ready. Extra args: request
              )


def execute_from_config(config_file):
    '''Create and run an :class:`App` from a ``config_file``.

This is the function to use when creating the script which runs your
web applications::

    import lux

    if __name__ == '__main__':
        lux.execute_from_config('path.to.config')

:param config_file: the python dotted path to the config file for setting
    up a new :class:`App`. The config file should be located in the
    python module which implements the :ref:`main application` of the web site.
    '''
    execute_app(App(config_file))


def execute_from_command_line(argv=None):
    '''Execute a command line command'''
    execute_app(App('lux.core.app'))


def execute_app(app, argv=None, **params):
    '''Execute a given ``app``.

    :parameter app: the :class:`.App` to execute
    :parameter argv: optional list of parameters, if not given ``sys.argv``
        is used instead.
    :parameter params: additional key-valued parameters to pass to the
        :class:`.Command` executing the ``app``.
    '''
    if argv is None:
        argv = sys.argv
    app.meta.argv = argv = list(argv)
    app.meta.script = argv.pop(0)
    # Parse for the command
    parser = app.get_parser(add_help=False)
    args, argr = parser.parse_known_args(argv)
    #
    # we have a command
    if args.command:
        try:
            command = app.get_command(args.command)
        except CommandError as e:
            print('\n'.join(('%s.' % e, 'Pass -h for list of commands')))
            exit(1)
        # Make sure the loop exists
        try:
            return command(argr, **params)
        except CommandError as e:
            print(str(e))
            exit(1)
    else:
        # this should fail unless we pass -h
        parser = app.get_parser(nargs=1)
        parser.parse_args(argv)


class App(ConsoleParser, LocalMixin, Extension):
    '''This is the main class for driving lux applications.

    It is a specialised :class:`~.Extension` which collects
    all extensions of your application and setup the wsgi middleware used by
    the web server.
    An :class:`App` is not initialised directly, the higher level
    :func:`execute_from_config` is used instead.


    .. attribute:: debug

        debug flag set at runtime via the ``debug`` flag::

            python myappscript.py serve --debug

    .. attribute:: auth_backend

        Used by the sessions extension

    '''
    debug = False
    admin = None
    auth_backend = None

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
        Parameter('ERROR_HANDLER', None,
                  'Handler of Http exceptions'),
        Parameter('HTML_HEAD_TITLE', 'Lux',
                  'Default HTML Title'),
        Parameter('LOGGING_CONFIG', None,
                  'Dictionary for configuring logging'),
        Parameter('MEDIA_URL', 'media',
                  'the base url for static files'),
        Parameter('MINIFIED_MEDIA', True,
                  'Use minified media files. All media files will replace '
                  'their extensions with .min.ext. For example, javascript '
                  'links *.js become *.min.js'),
        Parameter('HTML_LINKS', [],
                  'List of links to include in the html head tag.'),
        Parameter('JSREQUIRED', ('require',),
                  'Default Required javascript. Loaded via requirejs.'),
        Parameter('JSREQUIRE_CALLBACK', None,
                  'Callback used by requirejs.'),
        Parameter('HTML_META',
                  [{'http-equiv': 'X-UA-Compatible',
                    'content': 'IE=edge'},
                   {'name': 'viewport',
                    'content': 'width=device-width, initial-scale=1'}],
                  'List of default ``meta`` elements to add to the html head'
                  'element'),
        Parameter('DATE_FORMAT', '%Y %b %d %H:%M:%S',
                  'Default formatting for dates'),
        Parameter('DEFAULT_TEMPLATE_ENGINE', 'python',
                  'Default template engine'),
        Parameter('SITE_NAME', 'Lux', 'Web site name'),
        Parameter('SITE_URL', None,
                  'Web site url'),
        Parameter('LINKS',
                  {'python': 'https://www.python.org/',
                   'lux': 'https://github.com/quantmind/lux',
                   'pulsar': 'http://pythonhosted.org/pulsar'},
                  'Links used throughout the web site'),
        Parameter('CACHE_SERVER', None,
                  ('Cache server, can be a connection string to a valid '
                   'datastore which support the cache protocol or an object '
                   'supporting the cache protocol'))
        ]

    def __init__(self, config_file, **params):
        if not os.path.exists(config_file):
            config_file = import_module(config_file).__file__
        self._params = params
        self.configure(config_file)

    def __call__(self, environ, start_response):
        '''The WSGI thing.'''
        handler = self.handler
        request = self.wsgi_request(environ)
        if self.debug:
            self.logger.debug('Serving request %s' % request.path)
        self.fire('on_request', request)
        return handler(environ, start_response)

    @property
    def config_module(self):
        '''The :ref:`configuration file` used by this :class:`App`.'''
        return '%s.%s' % (self, self.meta.file.module_name())

    @property
    def logger(self):
        return self.local.logger

    @property
    def extensions(self):
        '''Ordered dictionary of :class:`.Extension` available.

        The order is the same as in the
        :ref:`EXTENSIONS config <configuration>` parameter.
        '''
        return self.config['EXTENSION_HANDLERS']

    @local_property
    def events(self):
        return {}

    @property
    def models(self):
        '''Registered models for this applications.

        Models are registered via the :mod:`lux.extensions.api` extension.
        '''
        return self.local.models

    @local_property
    def handler(self):
        '''The WSGI application handler for this :class:`App`.

        It is lazily loaded the first time it is accessed so that
        this :class:`App` can be used by pulsar in a multiprocessing setup.
        '''
        # do this here so that the config is already loaded before fire signal
        extensions = list(itervalues(self.extensions))
        self.fire('on_config')
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
        handler = WsgiHandler(middleware, response_middleware=rmiddleware)
        self.fire('on_loaded', handler)
        return handler

    def get_version(self):
        '''Get version of this :class:`App`. Required by
        :class:`.ConsoleParser`.'''
        return self.meta.version

    def wsgi_request(self, environ=None, loop=None, path=None, **kw):
        '''Create a :class:`WsgiRequest` from a wsgi ``environ`` and set the
        ``app`` attribute in the cache.
        Additional keyed-valued parameters can be inserted.
        '''
        if not environ:
            # No WSGI environment, build a test one
            environ = test_wsgi_environ(path=path, loop=loop)
        if kw:
            environ.update(kw)
        request = WsgiRequest(environ)
        environ['error.handler'] = self.config['ERROR_HANDLER']
        request.cache.app = self
        return request

    def html_document(self, request):
        '''Build the HTML document.

        Usually there is no need to call directly this method.
        Instead one can use the :attr:`.WsgiRequest.html_document`.
        '''
        content_type = request.response.content_type
        handler = request.app_handler
        title = None
        if handler:
            title = handler.parameters.get('title')
        cfg = self.config
        doc = HtmlDocument(title=title or cfg['HTML_HEAD_TITLE'],
                           media_path=cfg['MEDIA_URL'],
                           minified=cfg['MINIFIED_MEDIA'],
                           known_libraries=None,
                           scripts_dependencies=None,
                           require_callback=cfg['JSREQUIRE_CALLBACK'],
                           debug=self.debug,
                           content_type=content_type,
                           charset=cfg['ENCODING'])
        #
        if doc.has_default_content_type:
            head = doc.head
            #
            required = cfg['JSREQUIRED']
            if required:
                head.scripts.require(*required)
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

    @local_property
    def commands(self):
        '''Load all commands from installed applications'''
        # we need to make sure the middleware is loaded
        self.handler
        cmnds = OrderedDict()
        for e in self.config['EXTENSIONS']:
            try:
                modname = e + ('.core' if e == 'lux' else '') + '.commands'
                mod = import_module(modname)
                if hasattr(mod, '__path__'):
                    path = mod.__path__[0]
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

    @local_property
    def config(self):
        '''The :ref:`configuration <configuration>` dictionary for this
        :class:`App`.

        Evaluated lazily when :attr:`extensions` are loaded.
        '''
        parser = self.get_parser(with_commands=False, add_help=False)
        options, _ = parser.parse_known_args(self.meta.argv)
        config_module = import_module(options.config)
        if options.config != self.config_module:
            # Different config file, configure again
            self.configure(config_module.__file__)
        #
        # setup application
        config = self.setup(config_module, options.debug, options.loglevel,
                            self._params)
        #
        # Load extensions
        self.logger.debug('Setting up extensions')
        apps = list(config['EXTENSIONS'])
        add_app(apps, 'lux', 0)
        add_app(apps, self.meta.name)
        config['MEDIA_URL'] = remove_double_slash('/%s/' % config['MEDIA_URL'])
        config['EXTENSIONS'] = tuple(apps)
        config['EXTENSION_HANDLERS'] = extensions = OrderedDict()
        for name in config['EXTENSIONS'][1:]:
            Ext = self.load_extension(name)
            if Ext:
                extension = Ext()
                extensions[extension.meta.name] = extension
                self.bind_events(extension)
                config.update(extension.setup(config_module, options.debug,
                                              options.loglevel, self._params))
        return config

    def get_command(self, name, stdout=None, stderr=None):
        '''Construct and return a :class:`Command` for this application.'''
        commands = {}
        for e, cmnds in self.commands.items():
            for cmnd in cmnds:
                if name == cmnd:
                    modname = 'lux.core' if e == 'lux' else e
                    mod = import_module('%s.commands.%s' % (modname, name))
                    return mod.Command(name, self, stdout, stderr)
        raise CommandError("Unknown command '%s'" % name)

    def get_usage(self):
        '''Returns the script's main help text, as a string.'''
        description = self.config['DESCRIPTION'] or 'Lux web-framework'
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
        parser = super(App, self).get_parser(**params)
        parser.add_argument('command', nargs=nargs, help='command to run')
        return parser

    def on_start(self, server):
        self.fire('on_start', server)

    def render_error(self, environ, response, trace):
        if self.debug:
            return render_trace(environ, response, trace)

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

    def configure(self, file):
        # Check if an extension module is available
        self.meta = self.meta.copy(file)
        self.meta.path.add2python(self.meta.name, up=1)
        extension = self.load_extension(self.meta.name)
        if extension:   # extension available, get the version from it
            self.meta.version = extension.meta.version
        if not self.meta.has_module:
            raise RuntimeError('Invalid project setup. The Application '
                               'config module must be within a valid python '
                               'module.')

    def fire(self, event, *args):
        '''Fire an ``event``.'''
        handlers = self.events.get(event)
        if handlers:
            for handler in handlers:
                handler(self, *args)

    def setup_logger(self, config, debug, loglevel):
        self.debug = debug
        log_config = config['LOGGING_CONFIG']
        self.local.logger = logging.getLogger('lux')

    def bind_events(self, extension):
        events = self.events
        for name in ALL_EVENTS:
            if name not in events:
                events[name] = []
            handlers = events[name]
            if hasattr(extension, name):
                handlers.append(getattr(extension, name))

    def format_date(self, dte):
        return dte.strftime(self.config['DATE_FORMAT'])

    def clone(self):
        return pickle.loads(pickle.dumps(self))

    def template(self, name):
        '''Load a template from the file system
        '''
        for ext in reversed(self.extensions.values()):
            filename = os.path.join(ext.meta.path, 'templates', name)
            if os.path.exists(filename):
                with open(filename, 'r') as file:
                    return file.read()

    def context(self, request, context, js=None):
        '''Load the ``context`` dictionary for this ``request``
        '''
        context = context or {}
        method = 'jscontext' if js else 'context'
        for ext in self.extensions.values():
            if hasattr(ext, method):
                getattr(ext, method)(request, context)
        return context

    def html_response(self, request, template_name, context=None,
                      jscontext=None, title=None):
        '''Html response via a template.

        :param request: the :class:`.WsgiRequest`
        :param template_name: the template file name to load
        :param context: optional context dictionary
        '''
        if request.response.content_type == 'text/html':
            document = request.html_document
            head = document.head
            if title:
                head.title = title % head.title
            context = self.context(request, context)
            jscontext = self.context(request, jscontext, 'js')
            if jscontext:
                jscontext = json.dumps(jscontext)
                head.embedded_js.append('var context=%s;' % jscontext)
            template = self.template(template_name)
            if context:
                rnd = template_engine(self.config['DEFAULT_TEMPLATE_ENGINE'])
                template = rnd(template, context)
            document.body.append(template)
            return document.http_response(request)


def add_app(apps, name, pos=None):
    '''Insert a name to the list'''
    try:
        apps.remove(name)
    except ValueError:
        pass
    if pos is not None:
        apps.insert(pos, name)
    else:
        apps.append(name)
