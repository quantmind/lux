import sys
from copy import copy

from pulsar.apps.wsgi import LazyWsgi

from .commands import CommandError, service_parser
from .app import Application


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
