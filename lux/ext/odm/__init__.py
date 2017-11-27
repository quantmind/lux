"""
Lux extension for integrating SQL and NoSQL databases into applications.

The extension create a new application method called ``odm``
which can be used to access object data mapper for different backend.

It requires the :mod:`lux.extensions.rest` module and pulsar-odm_ which is
built on top of sqlalchemy, pulsar and greenlet.

_ ..pulsar-odm: https://github.com/quantmind/pulsar-odm
"""
from sqlalchemy.ext.serializer import dumps

from odm.mapper import object_session, declared_attr

from lux.core import Parameter, LuxExtension

from .mapper import Mapper, model_base
from .models import Model
from .fields import Related
from .migrations import migrations


__all__ = ['model_base',
           'ModelSchema',
           'declared_attr',
           'Model',
           'Related',
           'migrations',
           'object_session']


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
                  'operator'),
        Parameter('CHANNEL_DATAMODEL', 'datamodel',
                  'Channel name for data models updates'),
    ]

    def on_config(self, app):
        '''Initialise Object Data Mapper'''
        self.require(app, 'lux.ext.rest')
        app.odm = Odm(app)

    def on_after_flush(self, app, session):
        """broadcast models events into the data-models channel

        channel: data-models
        event: <model-identifier>.<event>
        data: JSON representation of model

        <event> is one of ``create``, ``update``, ``delete``
        """
        request = session.request
        if not app.channels or not request:
            return
        for instance, event in session.changes():
            app.channels.publish(
                app.config['CHANNEL_DATAMODEL'],
                '%s.%s' % (instance.__class__.__name__.lower(), event),
                dumps(instance)
            )

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
