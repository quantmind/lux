from pulsar import Setting

import lux


class Command(lux.Command):
    option_list = (
        Setting('force', ('--force',),
                action='store_true',
                default=False,
                desc='remove pre-existing tables if required'),
        Setting('apps', nargs='*',
                desc='appname appname.ModelName ...'),
    )
    help = ("create database tables for registered models.")
    args = '[appname appname.ModelName ...]'

    def __call__(self, argv, **params):
        return self.run_until_complete(argv, **params)

    def run(self, argv):
        options = self.options(argv)
        apps = options.apps
        models = self.app.models
        for model in models:
            manager = models[model]
            result = yield from manager.create_table(
                remove_existing=options.force)
            self.write('Created table for %s' % manager)
