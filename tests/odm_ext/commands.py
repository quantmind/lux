from lux.utils import test


class ApiCommandsTest(test.TestCase):
    config_file = 'tests.odm_ext'

    def test_command_flushdb(self):
        app = self.application()
        yield from self.run_command(app, 'create_databases')
        yield from self.run_command(app, 'create_tables')
        yield from self.run_command(app, 'flushdb')

        mapper = app.mapper()
        self.assertEqual(len(mapper), 4)
        tables = yield from mapper.default_store.table_all()
        self.assertEqual(len(tables), 4)

    def __test_dumpdb_command(self):
        cmnd = self.fetch_command('dumpdb')
