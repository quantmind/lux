from lux.utils import test


class TestSockJSRestApp(test.AppTestCase):
    config_file = 'tests.sockjs'

    def test_app(self):
        from lux.extensions.sockjs import LuxWs
        app = self.app
        self.assertEqual(app.config['WS_URL'], '/testws')
        handler = app.extensions['lux.extensions.sockjs'].websocket
        self.assertEqual(handler.pubsub, None)
        self.assertIsInstance(handler, LuxWs)

    def test_get(self):
        request = self.client.get('/testws')
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type,
                         'text/plain; charset=utf-8')

    def test_info(self):
        request = self.client.get('/testws/info')
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type,
                         'application/json; charset=utf-8')
