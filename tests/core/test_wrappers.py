from lux.utils import test


class TestWrappers(test.TestCase):
    config_file = 'tests.core'

    async def test_is_secure(self):
        app = self.application()
        client = self.app_client(app)
        request = await client.get('/')
        self.assertFalse(request.is_secure)

    async def test_logger(self):
        app = self.application()
        client = self.app_client(app)
        request = await client.get('/')
        self.assertNotEqual(app.logger, request.logger)
