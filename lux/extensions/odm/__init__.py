'''
Lux extension for integrating SQL and NoSQL into applications.

The extension create create a new application attribute called ``odm``
which can be used to access object data mappers for different backend.
To access the ``sql`` mapper:

    sql = app.odm('sql')

in a router handler:

    def get(self, request):
        sql = request.app.odm('sql')
        with sql.session().begin() as session:
            ...
'''
import lux
from lux import Parameter

from pulsar.utils.log import LocalMixin

from .exc import *
from .mapper import Mapper, Model
from .views import CRUD, RestRouter
from .models import RestModel
from .forms import RelationshipField, UniqueField


class Extension(lux.Extension):
    '''Object data mapper extension

    Uses pulsar-odm for sychronous & asynchronous data mappers
    '''
    _config = [
        Parameter('DATASTORE', None,
                  'Dictionary for mapping models to their back-ends database'),
        Parameter('DATABASE_SESSION_SIGNALS', True,
                  'Register event handlers for database session')
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
        odm = self()
        if self.app.green_pool:
            tables = yield from self.app.green_pool.submit(odm.tables)
        else:
            tables = odm.tables()
        return tables
