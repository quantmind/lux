import re
import os
import logging
from copy import copy
from contextlib import contextmanager
from inspect import ismodule
from importlib import import_module
from itertools import chain

from sqlalchemy import MetaData, Table, inspect, event, exc
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.session import Session

from pulsar import ImproperlyConfigured
from pulsar.apps.data import Store, create_store
from pulsar.apps.greenio import wait


_camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')

logger = logging.getLogger('lux.odm')


class BaseModel(object):

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()


Model = declarative_base(cls=BaseModel)


class Mapper:
    '''SQLAlchemy wrapper for lux applications
    '''

    def __init__(self, app, binds):
        self.app = app
        self._autodiscover(binds)

    def __getitem__(self, model):
        return self._declarative_register[model]

    def __getattr__(self, name):
        if name in self._declarative_register:
            return self._declarative_register[name]
        raise AttributeError('No model named "%s"' % name)

    def database_create(self, database, **params):
        '''Create databases for each engine and return a new :class:`.Mapper`.
        '''
        binds = {}
        dbname = database
        for key, engine in self.keys_engines():
            if hasattr(database, '__call__'):
                dbname = database(engine)
            assert dbname, "Cannot create a database, no db name given"
            key = key if key else 'default'
            binds[key] = self._database_create(engine, dbname)
        return self.__class__(self.app, binds)

    def database_all(self):
        '''Return a dictionary mapping engines with databases
        '''
        all = {}
        for engine in self.engines():
            all[engine] = self._database_all(engine)
        return all

    def database_drop(self, database=None, **params):
        dbname = database
        for engine in self.engines():
            if hasattr(database, '__call__'):
                dbname = database(engine)
            assert dbname, "Cannot drop database, no db name given"
            self._database_drop(engine, dbname)

    def tables(self):
        tables = []
        for engine in self.engines():
            tbs = engine.table_names()
            if tbs:
                tables.append((str(engine.url), tbs))
        return tables

    def table_create(self, remove_existing=False):
        """Creates all tables.
        """
        for engine in self.engines():
            tables = self._get_tables(engine)
            if not remove_existing:
                self.metadata.create_all(engine, tables=tables)
            else:
                pass

    def table_drop(self):
        """Drops all tables.
        """
        for engine in self.engines():
            self.metadata.drop_all(engine, tables=self._get_tables(engine))

    def reflect(self, bind='__all__'):
        """Reflects tables from the database.
        """
        self._execute_for_all_tables(bind, 'reflect', skip_tables=True)

    @contextmanager
    def begin(self, close=True, expire_on_commit=False, **options):
        """Provide a transactional scope around a series of operations.

        By default, ``expire_on_commit`` is set to False so that instances
        can be used outside the session.
        """
        session = self.session(expire_on_commit=expire_on_commit, **options)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            if close:
                session.close()

    def session(self, **options):
        options['binds'] = self.binds
        return LuxSession(self, **options)

    def get_engine(self, key=None):
        '''Get an engine by key
        '''
        if key in self._engines:
            return self._engines[key]
        elif key in self._nosql_engines:
            return self._nosql_engines[key]

    def engines(self):
        return chain(self._engines.values(), self._nosql_engines.values())

    def keys_engines(self):
        return chain(self._engines.items(), self._nosql_engines.items())

    def close(self):
        for engine in self.engines():
            engine.dispose()

    # INTERNALS
    def _get_tables(self, engine):
        tables = []
        for table, eng in self.binds.items():
            if eng == engine:
                tables.append(table)
        return tables

    def _database_all(self, engine):
        if isinstance(engine, Store):
            return engine.database_all()
        elif engine.name == 'sqlite':
            database = engine.url.database
            if os.path.isfile(database):
                return [database]
            else:
                return []
        else:
            insp = inspect(engine)
            return insp.get_schema_names()

    def _database_create(self, engine, dbname):
        if isinstance(engine, Store):
            return wait(engine.database_create(dbname))
        elif engine.name != 'sqlite':
            conn = engine.connect()
            # the connection will still be inside a transaction,
            # so we have to end the open transaction with a commit
            conn.execute("commit")
            conn.execute('create database %s' % dbname)
            conn.close()
        url = copy(engine.url)
        url.database = dbname
        return str(url)

    def _database_drop(self, engine, database):
        logger.info('dropping database "%s" from %s', database, engine)
        if engine.name == 'sqlite':
            try:
                os.remove(database)
            except FileNotFoundError:
                pass
        elif isinstance(engine, Store):
            engine.database_drop(database)
        else:
            conn = engine.connect()
            conn.execute("commit")
            conn.execute('drop database %s' % database)
            conn.close()

    def _autodiscover(self, binds):
        # Setup mdoels and engines
        if not binds:
            binds = {}
        elif isinstance(binds, str):
            binds = {'default': binds}
        if binds and 'default' not in binds:
            raise ImproperlyConfigured('default datastore not specified')

        self.metadata = MetaData()
        self._engines = {}
        self._nosql_engines = {}
        self._declarative_register = {}
        self.binds = {}
        # Create all sql engines in the binds dictionary
        # Quietly fails if the engine is not recognised,
        # it my be a NoSQL store
        for name, bind in tuple(binds.items()):
            key = None if name == 'default' else name
            try:
                self._engines[key] = create_engine(bind)
            except exc.NoSuchModuleError:
                self._nosql_engines[key] = create_store(bind)
        #
        if self._nosql_engines and not self.app.green_pool:
            raise ImproperlyConfigured('NoSql stores requires GREEN_POOL')

        for label, mod in module_iterator(self.app.config['EXTENSIONS']):
            # Loop through attributes in mod_models
            for name in dir(mod):
                value = getattr(mod, name)
                if isinstance(value, (Table, DeclarativeMeta)):
                    for table in value.metadata.sorted_tables:
                        if table.key not in self.metadata.tables:
                            engine = None
                            label = table.info.get('bind_label')
                            keys = ('%s.%s' % (label, table.key),
                                    label, None) if label else (None,)
                            for key in keys:
                                engine = self.get_engine(key)
                                if engine:
                                    break
                            assert engine
                            table.tometadata(self.metadata)
                            self.binds[table] = engine
                    if (isinstance(value, DeclarativeMeta) and
                            hasattr(value, '__table__')):
                        table = value.__table__
                        self._declarative_register[table.key] = value


class LuxSession(Session):
    """The sql alchemy session that lux uses.

    It extends the default session system with bind selection and
    modification tracking.
    """

    def __init__(self, mapper, **options):
        #: The application that this session belongs to.
        self.mapper = mapper
        if self.app.config['DATABASE_SESSION_SIGNALS']:
            self.register()
        super().__init__(**options)

    @property
    def app(self):
        return self.mapper.app

    def register(self):
        if not hasattr(self, '_model_changes'):
            self._model_changes = {}

        event.listen(self, 'before_flush', self.record_ops)
        event.listen(self, 'before_commit', self.record_ops)
        event.listen(self, 'before_commit', self.before_commit)
        event.listen(self, 'after_commit', self.after_commit)
        event.listen(self, 'after_rollback', self.after_rollback)

    @staticmethod
    def record_ops(session, flush_context=None, instances=None):
        try:
            d = session._model_changes
        except AttributeError:
            return

        for targets, operation in ((session.new, 'insert'),
                                   (session.dirty, 'update'),
                                   (session.deleted, 'delete')):
            for target in targets:
                state = inspect(target)
                key = state.identity_key if state.has_identity else id(target)
                d[key] = (target, operation)

    @staticmethod
    def before_commit(session):
        try:
            d = session._model_changes
        except AttributeError:
            return

        # if d:
        #     before_models_committed.send(session.app,
        #                                  changes=list(d.values()))

    @staticmethod
    def after_commit(session):
        try:
            d = session._model_changes
        except AttributeError:
            return

        # if d:
        #     models_committed.send(session.app, changes=list(d.values()))
        #     d.clear()

    @staticmethod
    def after_rollback(session):
        try:
            d = session._model_changes
        except AttributeError:
            return

        # d.clear()


def module_iterator(application):
    '''Iterate over applications modules
    '''
    if ismodule(application) or isinstance(application, str):
        if ismodule(application):
            mod, application = application, application.__name__
        else:
            try:
                mod = import_module(application)
            except ImportError:
                # the module is not there
                mod = None
        if mod:
            label = application.split('.')[-1]
            try:
                mod_models = import_module('.models', application)
            except ImportError:
                mod_models = mod
            label = getattr(mod_models, 'APP_LABEL', label)
            yield label, mod_models
    else:
        for app in application:
            yield from module_iterator(app)
