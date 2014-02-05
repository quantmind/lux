'''The :mod:`lux.core` module contains all the functionalities to run a
web site or an rpc server using lux and pulsar_.

ConsoleParser
=====================

.. autoclass:: ConsoleParser
   :members:
   :member-order: bysource


Command
==================

.. autoclass:: Command
   :members:
   :member-order: bysource

'''
import sys
import argparse
import logging

from pulsar import Setting, get_event_loop, new_event_loop, async, Application
from pulsar.utils.pep import native_str

from lux import __version__


__all__ = ['ConsoleParser',
           'CommandError',
           'Command',
           'execute_app']


class CommandError(Exception):
    pass


class ConsoleParser(object):
    '''A class for parsing the console inputs.'''
    help = None
    option_list = ()
    default_option_list = (
        Setting('loglevel',
                ('--log-level',),
                meta='LEVEL',
                default='info',
                desc='Set the overall log level.',
                choices=('debug', 'info', 'warning', 'error', 'critical')),
        Setting('debug',
                ('--debug',),
                action="store_true",
                default=False,
                desc='Run in debug mode.')
    )

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


class DummyApp(Application):

    def on_config(self, actor):
        return False


class Command(ConsoleParser):
    '''Signature class for lux commands. A :class:`Command` is never
    created directly, instead, the :meth:`App.get_command` method is used.

    .. attribute:: name

        Command name, given by the module name containing the Command.

    .. attribute:: app

        The :class:`App` running this :class:`Command`.

    .. attribute:: stdout

        The file object corresponding to the output streams of this command.

        Default: ``sys.stdout``

    .. attribute:: stderr

        The file object corresponding to the error streams of this command.

        Default: ``sys.stderr``
    '''
    def __init__(self, name, app, stdout=None, stderr=None):
        self.name = name
        self.app = app
        self.stdout = stdout
        self.stderr = stderr

    def __call__(self, argv, **params):
        return self.run(argv, **params)

    def get_version(self):
        """Return the :class:`Command` version.

        By default it is the same version as lux.
        """
        return __version__

    @property
    def config_module(self):
        return self.app.config_module

    def options(self, argv):
        '''parse the *argv* list and set up logger.

        Return the options namespace
        '''
        parser = self.get_parser(description=self.help or self.name)
        options = parser.parse_args(argv)
        return options

    def log_config(self):
        return {'root': {'handlers': ['console_message']}}

    def run(self, argv, **params):
        '''Run this :class:`Command`.

        This is the only method which needs implementing by subclasses.
        '''
        raise NotImplementedError

    def run_async(self, argv, **params):
        '''Run a command using pulsar asynchronous engine.'''
        loop = get_event_loop()
        run_until_complete = False
        if loop is None:
            run_until_complete = True
            loop = new_event_loop()
        future = async(self.run(argv, **params), loop)
        if run_until_complete:
            return loop.run_until_complete(future)
        else:
            return future

    @property
    def logger(self):
        return logging.getLogger('lux.command.%s' % self.name)

    def write(self, stream=''):
        '''Write ``stream`` to the :attr:`stdout`.'''
        h = self.stdout or sys.stdout
        if stream:
            h.write(native_str(stream))
        h.write('\n')

    def write_err(self, stream=''):
        '''Write ``stream`` to the :attr:`stderr`.'''
        h = self.stderr or self.stdout or sys.stderr
        if stream:
            h.write(native_str(stream))
        h.write('\n')

    def pulsar_app(self, argv, application=None):
        if application is None:
            application = DummyApp
        app = self.app
        return application(callable=app,
                           desc=app.config.get('DESCRIPTION'),
                           epilog=app.config.get('EPILOG'),
                           argv=argv,
                           version=app.meta.version,
                           debug=app.debug,
                           config=app.config_module)

    def pulsar_cfg(self, argv):
        app = self.pulsar_app(argv)
        app()
        return app.cfg


def execute_app(app, argv=None, **params):
    '''Execute a command for a given ``app``.
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
        try:
            return command(argr, **params)
        except CommandError as e:
            print(str(e))
            exit(1)
    else:
        # this should fail unless we pass -h
        parser = app.get_parser(nargs=1)
        parser.parse_args(argv)
