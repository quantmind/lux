import unittest
import mock

from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext import testbed

import lux


class TestCase(unittest.TestCase):
    '''Utility class for testing with GAE an lux'''
    config_module = None

    def app(self, **params):
        return lux.App(self.config_module, **params).setup()

    def request_start_response(self, app, **params):
        request = app.wsgi_request(**params)
        start_response = mock.MagicMock()
        return request, start_response

    def response(self, app=None, **params):
        if not app:
            app = self.app()
        request, sr = self.request_start_response(app, **params)
        response = app(request.environ, sr)
        self.assertEqual(response, request.response)
        return request

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()
