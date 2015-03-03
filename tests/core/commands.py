import os
import io
import shutil
from os import path

from lux.utils import test


class CommandTests(test.TestCase):
    config_file = 'tests.config'

    def test_startproject(self):
        command = self.fetch_command('start_project')
        self.assertTrue(command.help)
        name = 'testproject'
        try:
            yield from command([name])
            target = command.target
            self.assertTrue(path.isdir(target))
            self.assertTrue(path.isfile(path.join(target, 'manage.py')))
            self.assertTrue(path.isfile(path.join(target, 'Gruntfile.js')))
            self.assertTrue(path.isdir(path.join(target, name)))
        finally:
            shutil.rmtree(target)

    def test_serve(self):
        command = self.fetch_command('serve')
        self.assertTrue(command.help)
        self.assertEqual(len(command.option_list), 0)
        app = command(['-b', ':9000'], start=False)
        self.assertEqual(app, command.app)

    def test_generate_key(self):
        command = self.fetch_command('generate_secret_key')
        self.assertTrue(command.help)
        key = yield from command([])
        self.assertEqual(len(key), 50)
        key = yield from command(['--length', '35'])
        self.assertEqual(len(key), 35)
        key = yield from command(['--hex'])
        self.assertTrue(len(key) > 50)

    def test_show_parameters(self):
        command = self.fetch_command('show_parameters')
        self.assertTrue(command.help)
        yield from command([])
        data = command.app.stdout.getvalue()
        self.assertTrue(data)
