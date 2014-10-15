__test__ = False
import os
import io
import shutil
from os import path

import lux
from lux.utils import test


class CommandTests(test.TestCase):
    config_file = 'luxpy.config'

    def test_startproject(self):
        command = self.fetch_command('startproject')
        self.assertTrue(command.help)
        name = 'testproject'
        try:
            command([name])
            self.assertTrue(path.isdir(name))
            self.assertTrue(path.isfile(path.join(name, 'manage.py')))
            self.assertTrue(path.isfile(path.join(name, 'Gruntfile.js')))
            self.assertTrue(path.isdir(path.join(name, name)))
        finally:
            shutil.rmtree(name)

    def testServe(self):
        command = self.fetch_command('serve')
        self.assertTrue(command.help)
        self.assertEqual(command.app, self.application())
        self.assertEqual(len(command.option_list), 0)
        app = command([], start=False)

    def test_serve_dry(self):
        command = self.fetch_command('serve')
        server = command(['-b', '9000'], start=False)
        self.assertTrue(server)
        self.assertEqual(server.cfg.callable, self.application())

    def testShell(self):
        command = self.fetch_command('shell')
