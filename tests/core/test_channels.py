import asyncio
from unittest import skipUnless

from pulsar.apps.test import check_server

from lux.utils import test

from tests.config import redis_cache_server


REDIS_OK = check_server('redis')


@skipUnless(REDIS_OK, 'Requires a running Redis server')
class ChannelsTests(test.TestCase):
    config_file = 'tests.core'
    config_params = {'PUBSUB_STORE': redis_cache_server,
                     'APP_NAME': 'foooo'}

    def test_handler(self):
        app = self.application()
        self.assertFalse(app.channels is None)
        self.assertFalse(app.channels)

    async def test_ping(self):
        app = self.application()
        client = test.TestClient(app)
        request = await client.get('/')
        self.assertEqual(request.response.status_code, 404)
        self.assertTrue(app.channels)
        self.assertTrue('foooo-server' in app.channels)

    async def test_reload(self):
        app = self.application()
        client = test.TestClient(app)
        await client.get('/')
        # reload the app
        clear_local = app.callable.clear_local
        future = asyncio.Future()

        def fire():
            clear_local()
            future.set_result(None)

        app.callable.clear_local = fire
        res = await app.reload()
        self.assertTrue(res)
        await future
