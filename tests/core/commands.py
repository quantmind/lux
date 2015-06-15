import os
import io
import shutil
from os import path

from lux.utils import test


class CommandTests(test.TestCase):
    config_file = 'tests.config'

    @test.test_timeout(30)
    @test.green
    def test_startproject(self):
        command = self.fetch_command('start_project')
        self.assertTrue(command.help)
        name = test.randomname('sp')
        target = None
        try:
            command([name])
            target = command.target
            self.assertTrue(path.isdir(target))
            self.assertTrue(path.isfile(path.join(target, 'manage.py')))
            self.assertTrue(path.isfile(path.join(target, 'Gruntfile.js')))
            self.assertTrue(path.isdir(path.join(target, name)))
        finally:
            if target:
                shutil.rmtree(target)

    def test_serve(self):
        command = self.fetch_command('serve')
        self.assertTrue(command.help)
        self.assertEqual(len(command.option_list), 0)
        app = command(['-b', ':9000'], start=False)
        self.assertEqual(app, command.app)

    def test_command_write_err(self):
        command = self.fetch_command('serve')
        command.write_err('errore!')
        data = command.app.stderr.getvalue()
        self.assertTrue('errore!')

    def test_command_properties(self):
        app = self.application()
        command = self.fetch_command('serve')
        self.assertEqual(command.get_version(), app.get_version())
        self.assertEqual(command.config_module, app.config_module)

    @test.green
    def test_generate_key(self):
        command = self.fetch_command('generate_secret_key')
        self.assertTrue(command.help)
        key = command([])
        self.assertEqual(len(key), 50)
        key = command(['--length', '35'])
        self.assertEqual(len(key), 35)
        key = command(['--hex'])
        self.assertTrue(len(key) > 50)

    @test.green
    def test_show_parameters(self):
        command = self.fetch_command('show_parameters')
        self.assertTrue(command.help)
        command([])
        data = command.app.stdout.getvalue()
        self.assertTrue(data)
