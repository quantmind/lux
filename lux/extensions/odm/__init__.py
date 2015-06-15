'''
Lux extension for integrating SQL and NoSQL databases into applications.

The extension create a new application method called ``odm``
which can be used to access object data mapper for different backend.

It requires the :mod:`lux.extensions.rest` module and pulsar-odm_ which is
built on top of sqlalchemy, pulsar and greenlet.

_ ..pulsar-odm: https://github.com/quantmind/pulsar-odm
'''
import lux
from lux import Parameter

from pulsar.utils.log import LocalMixin

from .exc import *     # noqa
from .mapper import Mapper, model_base
from .views import CRUD, RestRouter
from .models import RestModel
from .forms import RelationshipField, UniqueField


__all__ = ['model_base', 'CRUD', 'RestRouter', 'RestModel',
           'RelationshipField', 'UniqueField']


class Extension(lux.Extension):
    '''Object data mapper extension

    Uses pulsar-odm for sychronous & asynchronous data mappers
    '''
    _config = [
        Parameter('DATASTORE', None,
                  'Dictionary for mapping models to their back-ends database'),
        Parameter('DATABASE_SESSION_SIGNALS', True,
                  'Register event handlers for database session'),
        Parameter('MIGRATIONS', None,
                  'Dictionary for mapping alembic settings')
    ]

    def on_config(self, app):
        '''Initialise Object Data Mapper'''
        app.odm = Odm(app, app.config['DATASTORE'])

    def on_loaded(self, app):
        '''When the application load, choose the
        concurrency paradigm
        '''
        odm = app.odm()
        if odm.is_green and not app.config['GREEN_POOL']:
            app.config['GREEN_POOL'] = 50


class Odm(LocalMixin):
    '''Lazy object data mapper container

    Usage:

        odm = app.odm()
    '''

    def __init__(self, app, binds):
        self.app = app
        self.binds = binds

    def __call__(self):
        if self.local.mapper is None:
            self.local.mapper = Mapper(self.app, self.binds)
        return self.local.mapper

    def database_create(self, database, **params):
        odm = Odm(self.app, self.binds)
        odm.local.mapper = self().database_create(database, **params)
        return odm

    def tables(self):
        '''Coroutine returning all tables managed by the mapper
        '''
        odm = self()
        if self.app.green_pool:
            tables = yield from self.app.green_pool.submit(odm.tables)
        else:
            tables = odm.tables()
        return tables
