from pulsar import ImproperlyConfigured

from lux.utils import test


class TestWrappers(test.TestCase):
    config_file = 'tests.core'

    def test_is_secure(self):
        app = self.application(SECURE_PROXY_SSL_HEADER=(
            'HTTP_X_FORWARDED_PROTO', 'https'))
        client = test.TestClient(app)
        request, _ = client.request_start_response('get', '/')
        self.assertFalse(request.is_secure)

    def test_is_secure_improperly_configured(self):
        app = self.application(
            SECURE_PROXY_SSL_HEADER='HTTP_X_FORWARDED_PROTO')
        client = test.TestClient(app)
        request, _ = client.request_start_response('get', '/')
        self.assertRaises(ImproperlyConfigured,
                          lambda: request.is_secure)

    def test_logger(self):
        app = self.application()
        client = test.TestClient(app)
        request, _ = client.request_start_response('get', '/')
        self.assertEqual(app.logger, request.logger)
