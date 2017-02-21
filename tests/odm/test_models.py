from urllib.parse import urlsplit

from pulsar.api import ImproperlyConfigured

from lux.utils import test
from lux.extensions.rest import DictModel

from tests.odm.utils import OdmUtils


class TestModels(OdmUtils, test.AppTestCase):

    def test_register_null(self):
        self.assertFalse(self.app.models.register(None))
        users = self.app.models['users']
        model = DictModel('user')
        self.assertNotEqual(self.app.models.register(model), model)
        self.assertEqual(self.app.models.register(model), users)
        self.assertEqual(self.app.models.register(lambda: model), users)
        self.assertRaises(ImproperlyConfigured, lambda: model.app)

    def test_api_url(self):
        users = self.app.models['users']
        self.assertTrue(users.api_route)
        request = self.app.wsgi_request()
        url = users.api_url(request)
        self.assertTrue(urlsplit(url).path, '/users')
