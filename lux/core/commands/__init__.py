import os
import argparse
import logging
from inspect import cleandoc, getdoc, getfile
from collections import OrderedDict
from importlib import import_module

from pulsar.utils.log import lazyproperty
from pulsar.api import Setting, Application, ImproperlyConfigured
from pulsar.utils.config import Config, LogLevel, Debug, LogHandlers
from pulsar.utils.slugify import slugify
from pulsar.apps.greenio import run_in_greenlet

from lux import __version__
from lux.utils.files import skipfile


SEP = '='*50


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


class CmdType(type):
    """Collects subcommands from methos starting with `command_`
    """
    def __new__(cls, name, bases, attrs):
        commands = {}
        for key, value in attrs.items():
            if key.startswith('command_') and hasattr(value, '__call__'):
                commands[key[8:]] = value
        attrs['commands'] = commands
        return super(CmdType, cls).__new__(cls, name, bases, attrs)


class ConsoleParser:
    '''A class for parsing the console inputs.

    Used as base class for both :class:`.LuxCommand` and :class:`.App`
    '''
    help = None
    commands = None
    description = None
    option_list = ()
    default_option_list = (LogLevel(),
                           LogHandlers(default=['console']),
                           Debug())

    @property
    def config_module(self):
        raise NotImplementedError

    def get_version(self):
        raise NotImplementedError

    def get_parser(self, description=None, **params):
        description = description or self.description
        parser = argparse.ArgumentParser(description=description, **params)
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


class LuxBaseCommand(ConsoleParser, metaclass=CmdType):
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

    def get_version(self):
        """Return the :class:`.LuxCommand` version.

        By default it is the same version as lux.
        """
        return __version__

    @property
    def config_module(self):
        return self.app.config_module

    @property
    def logger(self):
        return logging.getLogger('lux.%s' % self.name)

    def write(self, stream=''):
        '''Write ``stream`` to the :attr:`stdout`.'''
        self.app.write(stream)

    def write_err(self, stream=''):
        '''Write ``stream`` to the :attr:`stderr`.'''
        self.app.write_err(stream)

    def get_usage(self):
        usage = [
            '',
            SEP,
            '%s - %s' % (self.name, self.help or 'no description'),
            SEP,
            '',
            'List of available commands',
            '--------------------------'
        ]
        N = max((len(c) for c in self.commands))
        frmt = '% ' + str(N) + 's - %s'
        usage.extend((
            frmt % (name, doc_command(self.commands[name]))
            for name in sorted(self.commands)
        ))
        usage.append('')
        return usage

    def command(self, executable, argv, **kwargs):
        parser = argparse.ArgumentParser(description=doc_command(executable))
        settings = getattr(executable, 'settings', [])
        for setting in settings:
            setting.add_argument(parser, True)
        options = parser.parse_args(argv)
        args = []
        for setting in settings:
            value = getattr(options, setting.name, kwargs.get(setting.name))
            args.append(value)
        return executable(self, *args)

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


class LuxCommand(LuxBaseCommand):

    def __call__(self, argv, **params):
        if self.commands:
            if not argv or argv[0] not in self.commands:
                return self.write('\n'.join(self.get_usage()))
            return self.command(self.commands[argv[0]], argv[1:], **params)

        if not self.app.callable.command:
            self.app.callable.command = self.name
        pulsar_app = self.pulsar_app(argv)
        pulsar_app.cfg.daemon = False
        pulsar_app()
        return self.execute(self.run, pulsar_app.cfg, **params)

    def execute(self, command, *args, **params):
        result = self._execute(command, *args, **params)
        if not self.app._loop.is_running():
            result = self.app._loop.run_until_complete(result)
        return result

    @run_in_greenlet
    def _execute(self, command, *args, **params):
        assert self.app.request_handler()
        return command(*args, **params)

    def run(self, argv, **params):
        '''Run this :class:`.LuxCommand`.

        This is the only method which needs implementing by subclasses.
        '''
        raise NotImplementedError


class ConsoleMixin(ConsoleParser):

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
                pass  # No management module
        return OrderedDict(((e, cmnds[e]) for e in reversed(cmnds)))

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
                 SEP,
                 description,
                 SEP,
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


class option:

    def __init__(self, *flags, help=None, nargs=None, **kwargs):
        name = None
        oflags = []
        for flag in flags:
            if not flag.startswith('-'):
                name = flag
                if not nargs:
                    nargs = '?'
                    oflags = None
            else:
                if oflags is None:
                    raise ImproperlyConfigured(
                        'cannot mix positional and keyed-valued arguments'
                    )
                if flag.startswith('--') or not name:
                    name = slugify(flag, '_')
                oflags.append(flag)
        if not name:
            raise ImproperlyConfigured('options with no name')
        if help:
            kwargs['desc'] = help
        self.setting = Setting(name, oflags, nargs=nargs, **kwargs)

    def __repr__(self):
        return repr(self.setting)

    def __call__(self, method):
        settings = getattr(method, 'settings', [])
        settings.insert(0, self.setting)
        method.settings = settings
        return method


def doc_command(method):
    doc = cleandoc(getdoc(method)).strip()
    return ', '.join((v for v in (d.strip() for d in doc.split('\n')) if v))
