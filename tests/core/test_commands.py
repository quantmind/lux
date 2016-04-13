from unittest import mock
import shutil
from os import path

from lux.utils import test


class CommandTests(test.TestCase):
    config_file = 'tests.core'

    async def test_media(self):
        command = self.fetch_command('media')
        base = path.dirname(__file__)
        js = path.join(base, 'js-test')
        scss = path.join(base, 'scss-test')
        try:
            await command(['--js-src', js, '--scss-src', scss])
            self.assertTrue(path.isdir(js))
            self.assertTrue(path.isdir(scss))
        finally:
            if path.isdir(js):
                shutil.rmtree(js)
            if path.isdir(scss):
                shutil.rmtree(scss)

    async def test_start_project(self):
        command = self.fetch_command('start_project')
        self.assertTrue(command.help)
        name = test.randomname('sp')
        target = None
        try:
            await command([name])
            target = command.target
            self.assertTrue(path.isdir(target))
        finally:
            if target:
                shutil.rmtree(target)

    def test_serve(self):
        command = self.fetch_command('serve')
        self.assertTrue(command.help)
        self.assertEqual(len(command.option_list), 1)
        app = command(['-b', ':9000'], start=False)
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
        await command([])
        self.assertEqual(command.app.stderr.getvalue(),
                         'Pid file not available\n')
