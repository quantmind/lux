from . import OdmCommand


class Command(OdmCommand):
    help = ("create database tables for registered models.")

    def run(self, options, **params):
        apps = options.apps
        mapper = self.app.mapper()
        stores = set()
        for manager in mapper:
            store = manager._store
            databases = yield from store.database_all()
            if store.database not in databases:
                if not options.dry_run:
                    yield from store.database_create(options.force)
                self.write('Created database for %s' % store)
