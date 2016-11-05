from unittest import mock, skipUnless
import shutil
from os import path

from pulsar.apps.test import TestFailure
from pulsar.apps.test import check_server

from lux.utils import test
from lux.core import CommandError


REDIS_OK = check_server('redis')


class CommandTests(test.TestCase):
    config_file = 'tests.core'

    async def test_start_project(self):
        command = self.fetch_command('start_project')
        self.assertTrue(command.help)
        name = test.randomname('sp')
        target = None
        try:
            target = await command([name])
            self.assertTrue(path.isdir(target))
        finally:
            if target:
                shutil.rmtree(target)

    def test_serve(self):
        command = self.fetch_command('serve')
        self.assertTrue(command.help)
        self.assertEqual(len(command.option_list), 1)
        app = command(['-b', ':9000'], start=False, get_app=True)
        self.assertEqual(app, command.app)

    def test_command_write_err(self):
        command = self.fetch_command('serve')
        command.write_err('errore!')
        data = command.app.stderr.getvalue()
        self.assertEqual(data, 'errore!\n')

    def test_command_properties(self):
        app = self.application()
        command = self.fetch_command('serve')
        self.assertEqual(command.get_version(), app.get_version())
        self.assertEqual(command.config_module, app.config_module)

    async def test_generate_key(self):
        command = self.fetch_command('generate_secret_key')
        self.assertTrue(command.help)
        key = await command([])
        self.assertEqual(len(key), 50)
        key = await command(['--length', '35'])
        self.assertEqual(len(key), 35)
        key = await command(['--hex'])
        self.assertTrue(len(key) > 50)

    async def test_show_parameters(self):
        command = self.fetch_command('show_parameters')
        self.assertTrue(command.help)
        await command([])
        data = command.app.stdout.getvalue()
        self.assertTrue(data)

    async def test_stop(self):
        command = self.fetch_command('stop')
        self.assertTrue(hasattr(command.kill, '__call__'))
        command.kill = mock.MagicMock()
        self.assertTrue(command.help)
        try:
            await command([])
        except CommandError as exc:
            self.assertEqual(str(exc), 'Pid file not available')
        else:
            raise TestFailure('CommandError not raised')

    @skipUnless(REDIS_OK, 'Requires a running Redis server and '
                          'redis python client')
    async def test_clear_cache(self):
        redis = 'redis://%s' % self.cfg.redis_server
        command = self.fetch_command('clear_cache', CACHE_SERVER=redis)
        self.assertTrue(command.help)
        result = await command([])
        self.assertEqual(result, 0)
