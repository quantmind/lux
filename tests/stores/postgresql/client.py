'''Test PostgreSQL client.'''
from pulsar.utils.security import random_string, ascii_letters
from pulsar.apps.data import create_store

from lux.utils import test


@test.skipUnless(test.get_params('POSTGRESQL_SETTINGS'),
                 'POSTGRESQL_SETTINGS required in test_settings.py file.')
class TestCase(test.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_id = ('test_%s' % random_string(length=10)).lower()

    def abc(self):
        _, address, params = parse_connection_string(
            cls.cfg.get('POSTGRESQL_SETTINGS'), 0)
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
        return '%s_%s' % (cls.test_id, name)

    def test_create_engine(self):
        engine = create_engine(self.cfg.get('POSTGRESQL_SETTINGS'))
        self.assertEqual(engine.name, 'postgresql')
        self.assertIsInstance(engine.pool, SqlPool)

    def test_create_connection(self):
        engine = create_engine(self.cfg.get('POSTGRESQL_SETTINGS'),
                               database='postgres')
        conn = yield engine.connect()
        self.assertIsInstance(conn, Connection)
        name = self.name('bla')
        result = yield conn.execute('CREATE DATABASE %s;' % name)
        self.assertTrue(result)


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
