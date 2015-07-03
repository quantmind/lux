from pulsar import ImproperlyConfigured

from lux.utils import test


class TestWrappers(test.TestCase):
    config_file = 'tests.core'

    def test_is_secure(self):
        app = self.application(SECURE_PROXY_SSL_HEADER=(
            'HTTP_X_FORWARDED_PROTO', 'https'))
        request, _ = self.request_start_response(app)
        self.assertFalse(request.is_secure)

    def test_is_secure_improperly_configured(self):
        app = self.application(
            SECURE_PROXY_SSL_HEADER='HTTP_X_FORWARDED_PROTO')
        request, _ = self.request_start_response(app)
        self.assertRaises(ImproperlyConfigured,
                          lambda: request.is_secure)

    def test_logger(self):
        app = self.application()
        request, _ = self.request_start_response(app)
        self.assertEqual(app.logger, request.logger)
