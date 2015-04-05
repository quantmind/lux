import os
from copy import copy
from contextlib import contextmanager

from sqlalchemy import MetaData, Table, inspect, event, exc
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.session import Session

from pulsar.utils.exceptions import ImproperlyConfigured

from .mapper import Mapper


class SQL(Mapper):
    '''SQLAlchemy wrapper for lux applications
    '''
    metadata = None

    def database_create(self, database=None, **params):
        '''Create databases for each engine and return a new :class:`.SQL`
        mapper.
        '''
        binds = {}
        dbname = database
        self._setup()
        for key, engine in self._engines.items():
            if hasattr(database, '__call__'):
                dbname = database(engine)
            assert dbname, "Cannot create a database, no db name given"
            key = key if key else 'default'
            binds[key] = self._database_create(engine, dbname)
        return binds

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

    def register(self, mod_models, *args, **params):
        '''Register Tables from ``mod_model`` module
        '''
        self._setup()
        # Loop through attributes in mod_models
        for name in dir(mod_models):
            value = getattr(mod_models, name)
            if isinstance(value, (Table, DeclarativeMeta)):
                for table in value.metadata.sorted_tables:
                    key = table.key
                    if table.key not in self.metadata.tables:
                        engine = None
                        label = table.info.get('bind_label')
                        if label:
                            engine = self._engines.get(label)
                        if not engine:
                            engine = self._engines.get(None)
                        if engine:
                            table.tometadata(self.metadata)
                            self.binds[table] = engine

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
    def begin(self, **options):
        """Provide a transactional scope around a series of operations."""
        session = self.session(**options)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def session(self, **options):
        options['binds'] = self.binds
        return LuxSession(self, **options)

    def engines(self):
        self._setup()
        return self._engines.values()

    def close(self):
        for engine in self.engines():
            engine.dispose()

    # INTERNALS
    def _setup(self):
        # Setup SQL Alchemy engines
        if self.metadata is not None:
            return
        self.metadata = MetaData()
        binds = self.binds
        self._engines = {}
        self.binds = {}
        # Create all sql engines in the binds dictionary
        # Quietly fails if the engine is not recognised,
        # it my be a NoSQL store
        for name, bind in tuple(binds.items()):
            key = None if name == 'default' else name
            try:
                self._engines[key] = create_engine(binds[name])
            except exc.NoSuchModuleError:
                pass
            else:
                binds.pop(name)

    def _get_tables(self, engine):
        tables = []
        for table, eng in self.binds.items():
            if eng == engine:
                tables.append(table)
        return tables

    def _database_all(self, engine):
        if engine.name == 'sqlite':
            database = engine.url.database
            if os.path.isfile(database):
                return [database]
            else:
                return []
        else:
            insp = inspect(engine)
            return insp.get_schema_names()

    def _database_create(self, engine, dbname):
        if engine.name != 'sqlite':
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
        if engine.name == 'sqlite':
            try:
                os.remove(database)
            except FileNotFoundError:
                pass
        else:
            conn = engine.connect()
            conn.execute("commit")
            conn.execute('drop database %s' % database)
            conn.close()


class LuxSession(Session):
    """The sql alchemy session that lux uses.

    It extends the default session system with bind selection and
    modification tracking.
    """

    def __init__(self, mapper, **options):
        #: The application that this session belongs to.
        self.mapper = mapper
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

