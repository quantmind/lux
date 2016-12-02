import os
import sys
from copy import copy
from inspect import getfile
from collections import OrderedDict
from importlib import import_module

from pulsar.utils.log import lazyproperty
from pulsar.apps.wsgi import LazyWsgi

from lux.utils.files import skipfile

from .commands import ConsoleParser, CommandError, service_parser


def execute_from_config(config_file, description=None, argv=None,
                        services=None, cmdparams=None, **params):

    if services:
        p = service_parser(services, description, False)
        opts, argv = p.parse_known_args(argv)
        if not opts.service and len(argv) == 1 and argv[0] in ('-h', '--help'):
            service_parser(services, description).parse_known_args()
        config_file = config_file % (opts.service or services[0])
        if opts.service and description:
            description = '%s - %s' % (description, opts.service)

    if argv is None:
        argv = sys.argv[:]
        params['script'] = argv.pop(0)

    app = App(config_file, argv, **params)
    application = app.setup(handler=False)

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
        app.argv.remove(command.name)
        cmdparams = cmdparams or {}
        try:
            return command(app.argv, **cmdparams)
        except CommandError as e:
            print(str(e))
            exit(1)
    else:
        # this should fail unless we pass -h
        parser = application.get_parser(nargs=1, description=description)
        parser.parse_args(argv)


class App(LazyWsgi):

    def __init__(self, config_file, argv, script=None, config=None,
                 cfg=None, **kw):
        params = config or {}
        params.update(kw)
        self.params = params
        self.config_file = config_file
        self.script = script
        self.argv = argv
        self.command = None
        self.cfg = cfg

    def setup(self, environ=None, on_config=None, handler=True):
        from lux.core.app import Application
        app = Application(self)
        if on_config:
            on_config(app)
        if handler:
            app.wsgi_handler()
        return app

    def clone(self, **kw):
        params = self.params.copy()
        params.update(kw)
        app = copy(self)
        app.params = params
        app.argv = copy(app.argv)
        return app

    def close(self):
        return self.handler().close()


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
