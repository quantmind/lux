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
from .models import RestModel, RestColumn, ModelColumn
from .forms import RelationshipField, UniqueField


__all__ = ['model_base', 'CRUD', 'RestRouter', 'RestModel', 'RestColumn',
           'ModelColumn', 'RelationshipField', 'UniqueField']


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
                  'Dictionary for mapping alembic settings'),
        Parameter('DEFAULT_TEXT_SEARCH_CONFIG', 'english',
                  'Default config/language for :search operator full-text '
                  'search')
    ]

    def on_config(self, app):
        '''Initialise Object Data Mapper'''
        app.require('lux.extensions.rest')
        app.odm = Odm(app, app.config['DATASTORE'])
        app.add_events(('on_before_commit', 'on_after_commit'))


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
