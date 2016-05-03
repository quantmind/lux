"""
Lux extension for integrating SQL and NoSQL databases into applications.

The extension create a new application method called ``odm``
which can be used to access object data mapper for different backend.

It requires the :mod:`lux.extensions.rest` module and pulsar-odm_ which is
built on top of sqlalchemy, pulsar and greenlet.

_ ..pulsar-odm: https://github.com/quantmind/pulsar-odm
"""
from lux.core import Parameter, LuxExtension, app_attribute
from lux.extensions.rest import SimpleBackend

from odm import declared_attr

from .mapper import Mapper, model_base
from .views import CRUD, RestRouter
from .models import RestModel, RestColumn
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
                  'operator'),
        Parameter('PUBSUB_MODELS_BROADCAST', None,
                  'Set of channels to broadcast events'),
    ]

    def on_config(self, app):
        '''Initialise Object Data Mapper'''
        self.require(app, 'lux.extensions.rest')
        app.odm = Odm(app)
        app.add_events(('on_before_commit', 'on_after_commit'))

    def on_after_commit(self, app, session, changes):
        """
        Called before SQLAlchemy commit.

        :param app:         Lux app object
        :param session:     SQLAlchemy session
        :param changes:     dict of model changes
        """
        bmodels = broadcast_models(app)
        if not bmodels:
            return
        request = app.wsgi_request()
        request.cache.auth_backend = SimpleBackend()
        for instance, event in changes.values():
            name = instance.__class__.__name__.lower()
            models = bmodels.get(name)
            if not models:
                continue
            channels = app.channels
            event = sql_to_broadcast.get(event, event)
            for model in models:
                data = model.serialise(request, instance)
                channels.publish(model.identifier, event, data)


@app_attribute
def broadcast_models(app):
    channels = app.config['PUBSUB_MODELS_BROADCAST']
    models = {}
    if channels:
        for model in app.models.values():
            if model.identifier in channels:
                if model.name not in models:
                    models[model.name] = [model]
                else:
                    models[model.name].append(model)
    return models


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
