'''Test CouchDB client.'''
from pulsar.utils.security import random_string, ascii_letters
from pulsar.apps.data import create_store

from lux.utils import test


@test.skipUnless(test.get_params('COUCHDB_SETTINGS'),
                 'COUCHDB_SETTINGS required in test_settings.py file.')
class TestCase(test.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = CouchDb(cls.cfg.get('COUCHDB_SETTINGS'))
        cls.test_id = ('test_%s' % random_string(length=10)).lower()
        cls.created = []

    @classmethod
    def tearDownClass(cls):
        for db in cls.created:
            try:
                yield cls.client.deletedb(db)
            except CouchDbError:
                pass

    @classmethod
    def name(cls, name):
        return '%s_%s' % (cls.test_id, name)

    @classmethod
    def createdb(cls, name):
        name = cls.name(name)
        result = yield cls.client.createdb(name)
        if result['ok']:
            cls.created.append(name)

    #    DATABASE
    def test_info(self):
        result = yield self.client.info()
        self.assertTrue('version' in result)
        self.assertEqual(result['couchdb'], 'Welcome')

    def test_createdb(self):
        result = yield self.createdb('a')
        self.assertTrue(result['ok'])

    def test_createdb_illegal(self):
        yield self.async.assertRaises(CouchDbError,
                                      self.client.createdb, 'bla.foo')

    def test_delete_non_existent_db(self):
        name = ('r%s' % random_string()).lower()
        try:
            result = yield self.client.deletedb(name)
        except CouchDbError as e:
            pass
        else:
            assert False, 'CouchDbError not raised'

    def test_databases(self):
        dbs = yield self.client.databases()
        self.assertTrue(dbs)
        self.assertTrue('_users' in dbs)

    # DOCUMENTS
    def test_get_invalid_document(self):
        yield self.async.assertRaises(CouchDbNoDbError,
                                      self.client.get, 'bla', '234234')

    def test_create_document(self):
        result = yield self.createdb('test1')
        self.assertTrue(result['ok'])
        result = yield self.client.post(self.name('test1'),
                                        {'title': 'Hello World',
                                         'author': 'lsbardel'})
        self.assertTrue(result['ok'])
        id = result['id']
        doc = yield self.client.get(self.name('test1'), result['id'])
        data = doc['data']
        self.assertEqual(data['author'], 'lsbardel')
        self.assertEqual(data['title'], 'Hello World')
