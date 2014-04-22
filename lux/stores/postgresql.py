from pulsar.apps.data import register_store

from .sql import SqlStore


class PostgreSqlStore(SqlStore):

    @classmethod
    def register(cls):
        from pulsar.apps.greenio import pg
        pg.make_asynchronous()


register_store('postgresql',
               'lux.stores.postgresql.PostgreSqlStore')
