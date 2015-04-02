from pulsar import ImproperlyConfigured
from pulsar.apps.wsgi import WsgiHandler, wait_for_body_middleware
from pulsar.apps.greenio import WsgiGreen
from pulsar.utils.log import LocalMixin

import lux
from lux import Parameter
from lux.extensions.auth import RequirePermission

from .register import register_applications
from .store import Store, RemoteStore, create_store, register_store, Command
from .api import CRUD
from .backends import sql


class Extension(lux.Extension):
    '''Object data mapper extension
    '''
    _config = [
        Parameter('DATASTORE', None,
                  'Dictionary for mapping models to their back-ends database'),
        Parameter('SEARCHENGINE', None,
                  'Search engine for models'),
        Parameter('ADMIN_URL', None,
                  'Admin site url', True),
        Parameter('ADMIN_PERMISSIONS', 'admin',
                  'Admin permission name'),
        Parameter('GREEN_WSGI', 0,
                  'Run the WSGI handle in a pool of greenlet')]

    def on_config(self, app):
        app.odm = Odm(app)

    def on_loaded(self, app):
        '''Wraps the Wsgi handler into a greenlet friendly handler
        '''
        if app.config['GREEN_WSGI']:
            green = WsgiGreen(app.handler)
            self.logger.info('Setup green Wsgi handler')
            app.handler = WsgiHandler((wait_for_body_middleware, green),
                                      async=True)


class Odm(LocalMixin):
    '''Lazy object data mapper container

    Usage:

        sql = app.odm('sql')
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, key):
        if self.local.mappers is None:
            self.local.mappers = self._autodiscover()
        return self.local.mappers[key]

    def database_create(app, dry_run=False):
        mapper = app.mapper()
        for manager in mapper:
            store = manager._store
            databases = store.database_all()
            if store.database not in databases:
                if not dry_run:
                    store.database_create()
                app.write('Created database %s' % store)


    def database_drop(app, dry_run=False):
        mapper = app.mapper()
        for manager in mapper:
            store = manager._store
            databases = store.database_all()
            if store.database in databases:
                if not dry_run:
                    store.database_drop()
                app.write('Dropped database %s' % store)

    def _autodiscover(self):
        datastore = self.app.config['DATASTORE']
        if not datastore:
            return {}
        elif isinstance(datastore, str):
            datastore = {'default': datastore}
        if 'default' not in datastore:
            raise ImproperlyConfigured('default datastore not specified')

        return register_applications(datastore,
                                     self.app.config['EXTENSIONS'],
                                     green=self.app.config['GREEN_WSGI'])
