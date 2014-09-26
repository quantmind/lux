from io import StringIO

import lux

from pulsar import get_actor
from pulsar.apps.test import unittest, HttpTestClient, TestSuite
from pulsar.apps.test.plugins import bench, profile


def get_params(*names):
    cfg = get_actor().cfg
    values = []
    for name in names:
        value = cfg.get(name)
        if value:
            values.append(value)
        else:
            return None
    return values


skipUnless = unittest.skipUnless


class TestCase(unittest.TestCase):
    '''TestCase class for lux tests.

    It provides several utilities methods.
    '''
    config_file = 'tests.config'
    config_params = {}
    apps = None

    def application(self, config_file=None, argv=None, **params):
        '''Return an application for testing. Override if needed.
        '''
        kwargs = self.config_params.copy()
        kwargs.update(params)
        config_file = config_file or self.config_file
        if argv is None:
            argv = []
        if '--log-level' not in argv:
            argv.append('--log-level')
            levels = self.cfg.loglevel if hasattr(self, 'cfg') else ['none']
            argv.extend(levels)
        app = lux.App(config_file, argv=argv, **kwargs).setup()
        if self.apps is None:
            self.apps = []
        self.apps.append(app)
        return app

    def fetch_command(self, command, out=None):
        '''Fetch a command.'''
        out = out or StringIO()
        app = self.application()
        cmd = app.get_command(command, stdout=out)
        self.assertTrue(cmd.logger)
        self.assertEqual(cmd.name, command)
        return cmd
