'''
.. autoclass:: Command
   :members:
   :member-order: bysource

'''
import argparse
import logging
from functools import partial

from pulsar import (Setting, get_event_loop, Application, ImproperlyConfigured,
                    asyncio, Config, get_actor)
from pulsar.utils.config import Loglevel, Debug, LogHandlers

from lux import __version__


__all__ = ['ConsoleParser',
           'CommandError',
           'Command']


class CommandError(ImproperlyConfigured):
    pass


class ConsoleParser(object):
    '''A class for parsing the console inputs.

    Used as base class for both :class:`.Command` and :class:`.App`
    '''
    help = None
    option_list = ()
    default_option_list = (Loglevel(),
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
    name = 'lux'
    cfg = Config(include=('loglevel', 'loghandlers', 'debug', 'config'))

    def __call__(self, actor=None):
        try:
            return super(LuxApp, self).__call__(actor)
        except ImproperlyConfigured:
            actor = actor or get_actor()
            return self.on_config(actor)

    def on_config(self, actor):
        asyncio.set_event_loop(actor._loop)
        return False


class Command(ConsoleParser):
    '''Signature class for lux commands.

    A :class:`.Command` is never initialised directly, instead,
    the :meth:`.Application.get_command` method is used to retrieve it and
    executed by its callable method.

    .. attribute:: name

        Command name, given by the module name containing the Command.

    .. attribute:: app

        The :class:`.Application` running this :class:`.Command`.

    .. attribute:: stdout

        The file object corresponding to the output streams of this command.

        Default: ``sys.stdout``

    .. attribute:: stderr

        The file object corresponding to the error streams of this command.

        Default: ``sys.stderr``
    '''
    def __init__(self, name, app):
        self.name = name
        self.app = app

    def __call__(self, argv, **params):
        app = self.pulsar_app(argv)
        app()
        # make sure the handler is created
        self.app.get_handler()
        return self.run_until_complete(app.cfg, **params)

    def get_version(self):
        """Return the :class:`.Command` version.

        By default it is the same version as lux.
        """
        return __version__

    @property
    def config_module(self):
        return self.app.config_module

    def run(self, argv, **params):
        '''Run this :class:`Command`.

        This is the only method which needs implementing by subclasses.
        '''
        raise NotImplementedError

    def run_until_complete(self, options, **params):
        '''Execute the :meth:`run` method using pulsar asynchronous engine.

        Most commands are run using this method.
        '''
        pool = self.app.green_pool
        loop = get_event_loop()
        run = partial(self.run, options, **params)
        if pool:
            result = pool.submit(run)
        else:
            result = loop.run_in_executor(None, run)
        return result if loop.is_running() else loop.run_until_complete(result)

    @property
    def logger(self):
        return logging.getLogger('lux.%s' % self.name)

    def write(self, stream=''):
        '''Write ``stream`` to the :attr:`stdout`.'''
        self.app.write(stream)

    def write_err(self, stream=''):
        '''Write ``stream`` to the :attr:`stderr`.'''
        self.app.write_err(stream)

    def pulsar_app(self, argv, application=None, log_name='lux', **kw):
        app = self.app
        if application is None:
            application = LuxApp
        cfg = application.cfg.copy()
        for setting in self.option_list:
            cfg.settings[setting.name] = setting.copy()
        return application(callable=app.callable,
                           description=self.help,
                           epilog=app.config.get('EPILOG'),
                           cfg=cfg,
                           argv=argv,
                           log_name=log_name,
                           version=app.meta.version,
                           debug=app.debug,
                           config=app.config_module,
                           **kw)
