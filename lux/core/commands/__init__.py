'''
.. autoclass:: Command
   :members:
   :member-order: bysource

'''
import argparse
import logging

from pulsar import Setting, Application, ImproperlyConfigured, isawaitable
from pulsar.utils.config import Config, LogLevel, Debug, LogHandlers

from lux import __version__
from lux.utils.async import maybe_green


class ConfigError(Exception):

    def __init__(self, config_file):
        self.config_file = config_file


class CommandError(ImproperlyConfigured):
    pass


def service_parser(services, description, help=True):
    description = description or 'services to run'
    p = argparse.ArgumentParser(
        description=description, add_help=help)
    p.add_argument('service', nargs='?', choices=services,
                   help='Service to run')
    return p


class ConsoleParser:
    '''A class for parsing the console inputs.

    Used as base class for both :class:`.LuxCommand` and :class:`.App`
    '''
    help = None
    option_list = ()
    default_option_list = (LogLevel(),
                           LogHandlers(default=['console']),
                           Debug())

    @property
    def config_module(self):
        raise NotImplementedError

    def get_version(self):
        raise NotImplementedError

    def get_parser(self, **params):
        parser = argparse.ArgumentParser(**params)
        parser.add_argument('--version',
                            action='version',
                            version=self.get_version(),
                            help="Show version number and exit")
        config = Setting('config',
                         ('-c', '--config'),
                         default=self.config_module,
                         desc=('python dotted path to a Lux/Pulsar config '
                               ' file, where settings can be specified.'))
        config.add_argument(parser, True)
        for opt in self.default_option_list:
            opt.add_argument(parser, True)
        for opt in self.option_list:
            opt.add_argument(parser, True)
        return parser


class LuxApp(Application):

    def __call__(self):
        try:
            return super().__call__()
        except ImproperlyConfigured:
            pass

    def on_config(self, actor):
        """This is just a dummy app and therefore we don't want to add
        it to the arbiter monitor collection
        """
        return False


class LuxCommand(ConsoleParser):
    '''Signature class for lux commands.

    A :class:`.LuxCommand` is never initialised directly, instead,
    the :meth:`.Application.get_command` method is used instead.

    .. attribute:: name

        Command name, given by the module name containing the Command.

    .. attribute:: app

        The :class:`.Application` running this :class:`.LuxCommand`.

    .. attribute:: stdout

        The file object corresponding to the output streams of this command.

        Default: ``sys.stdout``

    .. attribute:: stderr

        The file object corresponding to the error streams of this command.

        Default: ``sys.stderr``
    '''
    pulsar_config_include = ('log_level', 'log_handlers', 'debug', 'config')

    def __init__(self, name, app):
        self.name = name
        self.app = app

    def __call__(self, argv, **params):
        if not self.app.callable.command:
            self.app.callable.command = self.name
        app = self.pulsar_app(argv)
        app.cfg.daemon = False
        app()
        # Make sure the wsgi handler is created
        assert self.app.wsgi_handler()
        result = maybe_green(self.app, self.run, app.cfg, **params)
        if isawaitable(result) and not self.app._loop.is_running():
            result = self.app._loop.run_until_complete(result)
        return result

    def get_version(self):
        """Return the :class:`.LuxCommand` version.

        By default it is the same version as lux.
        """
        return __version__

    @property
    def config_module(self):
        return self.app.config_module

    def run(self, argv, **params):
        '''Run this :class:`.LuxCommand`.

        This is the only method which needs implementing by subclasses.
        '''
        raise NotImplementedError

    @property
    def logger(self):
        return logging.getLogger('lux.%s' % self.name)

    def write(self, stream=''):
        '''Write ``stream`` to the :attr:`stdout`.'''
        self.app.write(stream)

    def write_err(self, stream=''):
        '''Write ``stream`` to the :attr:`stderr`.'''
        self.app.write_err(stream)

    def pulsar_app(self, argv, application=None, callable=None,
                   log_name='lux', config=None, **kw):
        app = self.app
        if application is None:
            application = LuxApp
            cfg = Config(include=self.pulsar_config_include)
        else:
            cfg = application.cfg.copy()
        for setting in self.option_list:
            cfg.settings[setting.name] = setting.copy()
        callable = callable or app.callable
        callable.cfg = cfg
        return application(callable=callable,
                           description=self.help,
                           epilog=app.config.get('EPILOG'),
                           cfg=cfg,
                           argv=argv,
                           log_name=log_name,
                           version=app.meta.version,
                           debug=app.debug,
                           config=config or app.config_module,
                           **kw)
