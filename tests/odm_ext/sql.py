from pulsar.apps.test import test_timeout

from lux.utils import test


class SqlCommandsTest(test.TestCase):
    config_file = 'tests.odm_ext'
    config_params = {'DATASTORE': 'sqlite:///test.db'}
    config_params = {'DATASTORE': 'postgresql://bmlltech:bmlltech-localdb@127.0.0.1:5432/bmll'}

    @test_timeout(30)
    def test_command_flushdb(self):
        app = self.application()
        yield from self.run_command(app, 'create_databases')
        yield from self.run_command(app, 'create_tables')
        yield from self.run_command(app, 'flushdb', interactive=False)
        mapper = app.mapper()
        self.assertEqual(len(mapper), 1)
        tables = yield from mapper.default_store.table_all()
        self.assertEqual(len(tables), 1)
