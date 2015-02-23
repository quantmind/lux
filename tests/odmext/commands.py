import string

from pulsar.apps.test import random_string

from lux.utils import test


def randomname():
    return random_string(min_len=8, max_len=8,
                         characters=string.ascii_letters)


class ApiCommandsTest(test.TestCase):
    config_file = 'luxpy.odmext'

    @classmethod
    def setUpClass(cls):
        cls.stores = []

    @classmethod
    def tearDownClass(cls):
        for store in cls.stores:
            yield from store.database_drop()

    def test_create_tables_command(self):
        cmnd = self.fetch_command('create_tables')
        mapper = cmnd.app.mapper
        self.assertEqual(len(mapper), 3)
        database = self.set_random_database(mapper)
        # create the random test database
        result = yield from mapper.default_store.database_create()
        self.stores.append(mapper.default_store)
        # execute the command
        yield from cmnd([])
        tables = yield from mapper.default_store.table_all()
        self.assertEqual(len(tables), 3)

    def test_dumpdb_command(self):
        cmnd = self.fetch_command('dumpdb')

    def test_flushdb_command(self):
        cmnd = self.fetch_command('flushdb')

    def set_random_database(self, mapper):
        name = randomname()
        mapper.default_store.database = name
        for manager in mapper:
            self.assertEqual(manager._store.database, name)
        return name
