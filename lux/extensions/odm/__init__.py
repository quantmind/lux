"""
Lux extension for integrating SQL and NoSQL databases into applications.

The extension create a new application method called ``odm``
which can be used to access object data mapper for different backend.

It requires the :mod:`lux.extensions.rest` module and pulsar-odm_ which is
built on top of sqlalchemy, pulsar and greenlet.

_ ..pulsar-odm: https://github.com/quantmind/pulsar-odm
"""
from odm import declared_attr

from lux.core import Parameter, LuxExtension
from lux.extensions.rest import AppRequest

from .mapper import Mapper, model_base
from .rest import CRUD, RestRouter
from .models import RestModel, RestColumn, odm_models
from .ws import WsModelRpc


__all__ = ['model_base',
           'declared_attr',
           'CRUD',
           'RestRouter',
           'RestModel',
           'RestColumn']


sql_to_broadcast = {'insert': 'create'}


class Extension(LuxExtension, WsModelRpc):
    """Object data mapper extension

    Uses pulsar-odm for sychronous & asynchronous data mappers
    """
    _config = [
        Parameter('DATASTORE', None,
                  'Dictionary for mapping models to their back-ends database'),
        Parameter('DATABASE_SESSION_SIGNALS', True,
                  'Register event handlers for database session'),
        Parameter('MIGRATIONS', None,
                  'Dictionary for mapping alembic settings'),
        Parameter('DEFAULT_TEXT_SEARCH_CONFIG', 'english',
                  'Default config/language for :search full-text search '
                  'operator')
    ]

    def on_config(self, app):
        '''Initialise Object Data Mapper'''
        self.require(app, 'lux.extensions.rest')
        app.odm = Odm(app)

    def on_after_commit(self, app, session, changes):
        """
        Called after SQLAlchemy commit, broadcast models events into channels

        :param app:         Lux app object
        :param session:     SQLAlchemy session
        :param changes:     dict of model changes
        """
        request = AppRequest(app)
        for instance, event in changes.values():
            name = instance.__class__.__name__.lower()
            model = odm_models(app).get(name)
            if model:
                event = sql_to_broadcast.get(event, event)
                data = model.tojson(request, instance, in_list=True, safe=True)
                app.channels.publish(model.identifier, event, data)


class Odm:
    """Lazy object data mapper container
    """
    mapper = None

    def __init__(self, app):
        self.app = app

    @property
    def binds(self):
        return self.app.config['DATASTORE']

    def __call__(self):
        if self.mapper is None:
            self.mapper = Mapper(self.app, self.binds)
        return self.mapper

    def close(self):
        if self.mapper:
            self.mapper.close()

    def database_create(self, database, **params):
        odm = self.__class__(self.app)
        odm.mapper = self().database_create(database, **params)
        return odm

    async def tables(self):
        '''Coroutine returning all tables managed by the mapper
        '''
        odm = self()
        if self.app.green_pool:
            tables = await self.app.green_pool.submit(odm.tables)
        else:
            tables = odm.tables()
        return tables
