from lux.utils import test


class TestSockJSRestApp(test.AppTestCase):
    config_file = 'tests.sockjs'

    def test_app(self):
        app = self.app
        self.assertEqual(app.config['WS_URL'], '/testws')
        self.assertEqual(app.pubsub_store, None)

    def test_get(self):
        request = yield from self.client.get('/testws')
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type,
                         'text/plain; charset=utf-8')

    def test_info(self):
        request = yield from self.client.get('/testws/info')
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type,
                         'application/json; charset=utf-8')

    def test_websocket(self):
        request = yield from self.client.get('/testws/websocket')
        response = request.response
        self.assertEqual(response.status_code, 400)
