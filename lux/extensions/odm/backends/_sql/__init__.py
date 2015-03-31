import os

from sqlalchemy import inspect
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from .model import sql, SqlModelType, SqlManager, in_executor
from ...store import RemoteStore, ModelTypes, register_store, ascoro


ModelTypes.add(SqlModelType)


class SqlStore(RemoteStore):
    '''A pulsar :class:`.Store` based on sqlalchemy
    '''
    ModelType = SqlModelType
    default_manager = SqlManager

    def _init(self, **kwargs):
        dns = self._buildurl()
        self.sql_engine = create_engine(dns, **kwargs)
        self.session = sessionmaker(bind=self.sql_engine)

    def connect(self):
        return self.sql_engine.connect()

    def ping(self):
        with self.connect() as conn:
            r = conn.execute('select 1;')
            result = r.fetchone()
            return ascoro(result[0] == 1)

    # Database API
    def database_create(self, dbname=None, **kw):
        '''Create a new database
        '''
        dbname = dbname or self.database
        if not dbname:
            raise ValueError('Database name must be specified')
        if self.name != 'sqlite':
            with self.sql_engine.connect() as conn:
                result = conn.execute('CREATE DATABASE %s' % dbname)
        return ascoro(dbname)

    def database_all(self):
        '''Create a new database
        '''
        if self.name == 'sqlite':
            return ascoro([self.database])
        else:
            insp = inspect(self.sql_engine)
            return ascoro(insp.get_schema_names())

    def database_drop(self, dbname=None, **kw):
        dbname = dbname or self.database
        if not dbname:
            raise ValueError('Database name must be specified')
        if self.name == 'sqlite':
            try:
                os.remove(dbname)
            except FileNotFoundError:
                pass
        else:
            with self.sql_engine.connect() as conn:
                result = conn.execute('DROP DATABASE %s' % dbname)
        return ascoro(dbname)

    # Table API
    def table_create(self, model, remove_existing=False):
        table = model.__table__
        return ascoro(table.create(self.sql_engine,
                                   checkfirst=remove_existing))

    def table_all(self):
        insp = inspect(self.sql_engine)
        return ascoro(insp.get_table_names())

    def table_drop(self, model, remove_existing=False):
        sql_model = self.sql_model(model)
        table = sql_model.__table__
        return table.drop(self.sql_engine, checkfirst=remove_existing)

    def close(self):
        # make sure no connections are opened
        self.sql_engine.dispose()


for name in ('sqlite', 'postgresql', 'mysql'):
    register_store(name, "lux.extensions.odm.backends.SqlStore")
