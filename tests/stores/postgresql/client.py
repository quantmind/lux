'''Test PostgreSQL client.'''
from pulsar.apps.data import create_store

from lux.utils import test

from example.luxweb import settings

psql = getattr(settings, 'POSTGRESQL_SETTINGS')


@test.skipUnless(
    psql, '"POSTGRESQL_SETTINGS" required in example.luxweb.settings file')
class TestCase(test.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.created = []
        cls.store = create_store(psql, database=cls.name('test'))
        assert cls.store.database == cls.name('test')
        return cls.createdb();

    @classmethod
    def tearDownClass(cls):
        for db in cls.created:
            yield cls.store.delete_database(db)

    @classmethod
    def createdb(cls, name=None):
        if name:
            name = cls.name(name)
        name = yield cls.store.create_database(name)
        cls.created.append(name)

    @classmethod
    def name(cls, name):
        return '%s_%s' % (cls.cfg.exc_id, name)

class d:

    def test_store(self):
        store = self.store
        self.assertEqual(store.name, 'postgresql')
        sql = store.sql_engine
        self.assertTrue(sql)

    def test_create_connection(self):
        from sqlalchemy.engine import Connection
        store = create_store(psql)
        conn = yield store.connect()
        self.assertIsInstance(conn, Connection)

    def test_create_table(self):
        result = yield self.store.create_table(User)
        #name = self.name('bla')
        #result = conn.execute('CREATE DATABASE %s;' % name)
        #self.assertTrue(result)
