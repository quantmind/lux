from lux.utils import test
from lux.extensions import api


class ApiCommandsTest(test.TestCase):
    config_file = 'luxpy.api'

    def test_create_tables_command(self):
        cmnd = self.fetch_command('create_tables')

    def test_dumpdb_command(self):
        cmnd = self.fetch_command('dumpdb')

    def test_flushdb_command(self):
        cmnd = self.fetch_command('flushdb')