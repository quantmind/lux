from . import OdmCommand


class Command(OdmCommand):
    help = ("create database tables for registered models.")

    def run(self, options, **params):
        apps = options.apps
        mapper = self.app.mapper()
        for manager in mapper:
            if not options.dry_run:
                result = yield from manager.table_create(options.force)
            self.write('Created table for %s' % manager)
