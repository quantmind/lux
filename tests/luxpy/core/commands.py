import os
import io
import shutil
from os import path

from lux.utils import test


class CommandTests(test.TestCase):
    config_file = 'luxpy.config'

    def test_startproject(self):
        command = self.fetch_command('startproject')
        self.assertTrue(command.help)
        name = 'testproject'
        try:
            command([name])
            target = command.target
            self.assertTrue(path.isdir(target))
            self.assertTrue(path.isfile(path.join(target, 'manage.py')))
            self.assertTrue(path.isfile(path.join(target, 'Gruntfile.js')))
            self.assertTrue(path.isdir(path.join(target, name)))
        finally:
            shutil.rmtree(target)

    def testServe(self):
        command = self.fetch_command('serve')
        self.assertTrue(command.help)
        self.assertEqual(len(command.option_list), 0)
        app = command([], start=False)

    def test_serve_dry(self):
        command = self.fetch_command('serve')
        server = command(['-b', '9000'], start=False)
        self.assertTrue(server)

    def testShell(self):
        command = self.fetch_command('shell')
