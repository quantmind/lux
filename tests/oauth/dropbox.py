'''Test Github API'''
from pulsar import get_actor
from pulsar.apps.http.auth import HTTPBasicAuth
from pulsar.apps.test import unittest

from lux.utils import test
from lux.extensions.services import api


@test.skipUnless(test.get_params('DROPBOX_CLIENT_ID',
                                 'DROPBOX_CLIENT_SECRET'),
                 'DROPBOX_* required in config.py file.')
class TestDropbox(test.TestCase):
    auth = None

    @classmethod
    def setUpClass(cls):
        cfg = cls.cfg
        d = Dropbox(client_id=cfg.get('DROPBOX_CLIENT_ID'),
                    client_secret=cfg.get('DROPBOX_CLIENT_SECRET'))
        cls.auth = yield d.authorization(response_type='code')
        # cls.auth = yield d.authorization(response_type='code',
        #                                redirect_uri='http://localhost:8060/')
        cls.dropbox = d

    def test_authorization(self):
        auth = self.auth
        self.assertTrue('id' in auth)
        self.assertTrue('token' in auth)
        self.assertEqual(auth['note'], 'Lux github test')
