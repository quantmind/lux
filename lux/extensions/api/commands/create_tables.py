import lux


class Command(lux.Command):
    option_list = (
        lux.Settings('apps', nargs='*',
                     desc='appname appname.ModelName ...'),
        lux.Settings('indent', ('--indent',),
                     default=-1, type=int,
                     desc=('Specifies the indent level to use when'
                           ' using json output.')),
        lux.Settings('format', ('-f', '--format'),
                     default='json',
                     desc='The data format.'),
        lux.Settings('target', ('-t', '--target'),
                     default='stdnetdump',
                     desc='Filename.'),
        lux.Settings('listall', ('-l', '--list-all'),
                     action='store_true',
                     default=False,
                     desc='List all supported formats and exit.'),
    )
    help = ("create database tables for registered models.")
    args = '[appname appname.ModelName ...]'

    def handle(self, argv, dump=True):
        options = self.options(argv)
        apps = options.apps or self.app.config.get('DUMPDB_EXTENSIONS')
        models = self.app.extensions['models'].get_router()
        models.create_all(apps)
