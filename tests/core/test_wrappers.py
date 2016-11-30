from lux.utils import test


class TestWrappers(test.TestCase):
    config_file = 'tests.core'

    def test_is_secure(self):
        app = self.application()
        client = test.TestClient(app)
        request, _ = client.request_start_response('get', '/')
        self.assertFalse(request.is_secure)

    def test_logger(self):
        app = self.application()
        client = test.TestClient(app)
        request, _ = client.request_start_response('get', '/')
        self.assertNotEqual(app.logger, request.logger)
