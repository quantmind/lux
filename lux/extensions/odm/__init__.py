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

from .mapper import Mapper, model_base
from .models import RestModel, RestField, odm_models


__all__ = ['model_base',
           'declared_attr',
           'RestModel',
           'RestField']


sql_delete = 'delete'


class Extension(LuxExtension):
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

    def on_before_commit(self, app, session):
        request = session.request
        if not request:
            return
        for instance in session.deleted:
            name = instance.__class__.__name__.lower()
            model = odm_models(app).get(name)
            if model:
                instance._json = model.tojson(
                    request, instance, in_list=True,
                    safe=True
                )

    def on_after_commit(self, app, session):
        """
        Called after SQLAlchemy commit, broadcast models events into channels

        :param app:         Lux app object
        :param session:     SQLAlchemy session
        :param changes:     dict of model changes
        """
        request = session.request
        if not request:
            return
        for instance, event in session.changes():
            name = instance.__class__.__name__.lower()
            model = odm_models(app).get(name)
            if model:
                if not hasattr(instance, '_json'):
                    data = model.tojson(
                        request, instance, in_list=True, safe=True)
                else:
                    data = instance._json
                app.channels.publish(model.identifier, event, data)

    def on_close(self, app):
        app.odm().close()


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
