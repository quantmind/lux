'''
Lux extension for integrating SQL and NoSQL databases into applications.

The extension create a new application method called ``odm``
which can be used to access object data mapper for different backend.

It requires the :mod:`lux.extensions.rest` module and pulsar-odm_ which is
built on top of sqlalchemy, pulsar and greenlet.

_ ..pulsar-odm: https://github.com/quantmind/pulsar-odm
'''
from lux.core import Parameter, LuxExtension
from lux.extensions.sockjs import broadcast
from lux.extensions.rest import SimpleBackend

from pulsar.utils.log import LocalMixin

from odm import declared_attr

from .exc import *     # noqa
from .mapper import Mapper, model_base
from .views import CRUD, RestRouter
from .models import RestModel, RestColumn, ModelColumn
from .forms import RelationshipField, UniqueField
from .ws import WsModelRpc


__all__ = ['model_base', 'declared_attr',
           'CRUD', 'RestRouter',
           'RestModel', 'RestColumn',
           'ModelColumn', 'RelationshipField', 'UniqueField']


sql_to_broadcast = {'insert': 'create'}


class Extension(LuxExtension, WsModelRpc):
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
                  'Default config/language for :search full-text search '
                  'operator')
    ]

    def on_config(self, app):
        '''Initialise Object Data Mapper'''
        app.require('lux.extensions.rest')
        app.odm = Odm(app, app.config['DATASTORE'])
        app.add_events(('on_before_commit', 'on_after_commit'))

    def on_after_commit(self, app, session, changes):
        """
        Called before SQLAlchemy commit.

        :param app:         Lux app object
        :param session:     SQLAlchemy session
        :param changes:     dict of model changes
        """
        broadcast_models = self.broadcast_models(app)
        if not broadcast_models:
            return
        request = app.wsgi_request()
        request.cache.auth_backend = SimpleBackend()
        for instance, event in changes.values():
            name = instance.__class__.__name__.lower()
            models = broadcast_models.get(name)
            if not models:
                continue
            event = sql_to_broadcast.get(event, event)
            for model in models:
                data = model.serialise(request, instance)
                broadcast(app, model.identifier, event, data)

    def broadcast_models(self, app):
        models = getattr(app, '_broadcast_models', None)
        if models is None:
            channels = app.config['BROADCAST_CHANNELS']
            models = {}
            if channels:
                for model in app.models.values():
                    if model.identifier in channels:
                        if model.name not in models:
                            models[model.name] = [model]
                        else:
                            models[model.name].append(model)
            app._broadcast_models = models
        return models


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

    async def tables(self):
        '''Coroutine returning all tables managed by the mapper
        '''
        odm = self()
        if self.app.green_pool:
            tables = await self.app.green_pool.submit(odm.tables)
        else:
            tables = odm.tables()
        return tables
