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

    def run(self, options, **params):
        apps = options.apps
        mapper = self.app.mapper
        for manager in mapper:
            result = yield from manager.table_create(options.force)
            self.write('Created table for %s' % manager)
