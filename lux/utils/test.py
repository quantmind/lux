import lux

from pulsar import get_actor
from pulsar.apps.test import unittest, HttpTestClient, TestSuite
from pulsar.apps.test.plugins import bench, profile
from pulsar.utils.httpurl import ispy3k
from pulsar.apps.wsgi import test_wsgi_environ

if ispy3k:
    from io import StringIO as Stream
else:   # pragma    nocover
    from io import BytesIO as Stream


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


def all_extensions():
    return ['lux.extensions.base',
            'lux.extensions.api',
            'lux.extensions.sessions',
            'lux.extensions.sitemap',
            'lux.extensions.cms',
            'lux.extensions.ui']


class TestCase(unittest.TestCase):
    '''TestCase class for lux tests. It provides several utilities methods.
    '''
    app = None
    config_file = 'tests.config'
    config_params = {}

    @classmethod
    def application(cls):
        '''Return an application for testing. Override if needed.
        '''
        if cls.app is None:
            cls.app = lux.App(cls.config_file, **cls.config_params)
        return cls.app

    def fetch_command(self, command, out=None):
        '''Fetch a command.'''
        out = out or Stream()
        app = self.application()
        cmd = app.get_command(command, stdout=out)
        self.assertTrue(cmd.logger)
        self.assertEqual(cmd.name, command)
        return cmd
