import unittest

from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext import testbed

from lux.utils import test


class TestCase(test.TestCase):
    '''Utility class for testing with GAE an lux
    '''
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
