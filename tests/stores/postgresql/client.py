'''Test PostgreSQL client.'''
from pulsar.apps.data import create_store

from lux.utils import test

from example.luxweb import settings

psql = getattr(settings, 'POSTGRESQL_SETTINGS')


@test.skipUnless(
    psql, '"POSTGRESQL_SETTINGS" required in example.luxweb.settings file')
class TestCase(test.TestCase):

    def abc(self):
        _, address, params = parse_connection_string(psql)
        cls.pool = PostgresPool()
        cls.client1 = cls.pool(address, **params)
        cls.test_id = ('test_%s' % random_string(length=10)).lower()
        cls.created = []
        yield cls.createdb('test1')
        params['db'] = cls.name('test1')
        cls.client = cls.pool(address, **params)

    @classmethod
    def __tearDownClass(cls):
        for db in cls.created:
            try:
                yield cls.client1.deletedb(db)
            except Exception:
                pass

    @classmethod
    def name(cls, name):
        return '%s_%s' % (cls.cfg.exec_id, name)

    def __test_create_store(self):
        store = create_store(psql)
        self.assertEqual(store.name, 'postgresql')
        sql = store.sql_engine
        self.assertTrue(sql)

    def test_create_connection(self):
        from sqlalchemy.engine import Connection
        store = create_store(psql)
        conn = yield store.connect()
        self.assertIsInstance(conn, Connection)
        #name = self.name('bla')
        #result = conn.execute('CREATE DATABASE %s;' % name)
        #self.assertTrue(result)

class d:
    @classmethod
    def createdb(cls, name):
        name = cls.name(name)
        yield cls.client1.createdb(name)
        cls.created.append(name)

    def test_client(self):
        client = self.client
        self.assertTrue(client.connection_pool)
        self.assertTrue(client.info)

    def test_create_db(self):
        result = yield self.createdb(self.name('test2'))
