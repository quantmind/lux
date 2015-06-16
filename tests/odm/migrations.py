import os
import os.path

from sqlalchemy.schema import MetaData

from lux.utils import test
from lux.core.commands import CommandError


class TestMigrationsCommands(test.TestCase):

    '''
    Test Lux commands wrapper for Alembic. Since Alembic has own tests,
    we only testing edge cases.
    '''
    config_file = 'tests.odm'
    config_params = {
        'DATASTORE': {
            'default': 'sqlite://',
            'auth': 'postgresql://lux:luxtest@127.0.0.1:5432/luxtests'
        },
        'MIGRATIONS': {
            'alembic': {
                'script_location': os.path.join(os.getcwd(), 'migrations')
            }
        }
    }

    def cmd(self):
        return self.fetch_command('alembic')

    def test_command_alembic(self):
        cmd = self.cmd()
        self.assertTrue(cmd.help)
        self.assertEqual(len(cmd.option_list), 4)

    def test_no_params(self):
        cmd = self.cmd()
        msg = 'Put [-l] for available commands'

        with self.assertRaises(CommandError) as e:
            yield from cmd([])
        self.assertEqual(str(e.exception), msg)

    def test_wrong_param(self):
        cmd = self.cmd()
        msg = 'Unrecognized command: test\nPut [-l] for available commands'

        with self.assertRaises(CommandError) as e:
            yield from cmd(['test'])
        self.assertEqual(str(e.exception), msg)

    def test_list_command(self):
        cmd = self.cmd()
        result = yield from cmd(['-l'])
        cmd_msg = 'Available commands:\n%s' % ', '.join(cmd.commands)
        self.assertEqual(result, cmd_msg)

    def test_missing_m_param(self):
        cmd = self.cmd()
        msg = 'Missing [-m] parameter for: auto'

        with self.assertRaises(CommandError) as e:
            yield from cmd(['auto'])
        self.assertEqual(str(e.exception), msg)

    def test_missing_revision_id(self):
        cmd = self.cmd()
        msg = 'Command: show required revision id'

        with self.assertRaises(CommandError) as e:
            yield from cmd(['show'])
        self.assertEqual(str(e.exception), msg)

    def test_missing_two_revisions_in_merge(self):
        cmd = self.cmd()
        msg = 'Command: merge required revisions id.'

        with self.assertRaises(CommandError) as e:
            yield from cmd(['merge', 'rev_id1', '-m', 'test'])
        self.assertEqual(str(e.exception), msg)

    def test_config(self):
        cmd = self.cmd()
        config = cmd.get_config()
        self.assertEquals(config.get_section_option('logging', 'path'), '')
        self.assertEqual(
            config.get_main_option('script_location'),
            os.path.join(os.getcwd(), 'migrations')
        )

    def test_metadata(self):
        cmd = self.cmd()
        metadata = cmd.get_config().metadata
        self.assertIsInstance(metadata, dict)
        for value in metadata.values():
            self.assertIsInstance(value, MetaData)

    def test_get_lux_template_directory(self):
        cmd = self.cmd()
        template_path = cmd.get_lux_template_directory()
        path = os.path.join(
            os.getcwd(),
            'lux/extensions/odm/commands/template'
        )
        self.assertEqual(template_path, path)
