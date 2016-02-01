import json
from lux.utils import test


class TestSockJSRestApp(test.AppTestCase):
    config_file = 'tests.sockjs'

    def ws(self):
        request = yield from self.client.wsget('/testws/websocket')
        return self.ws_upgrade(request.response)

    def test_app(self):
        app = self.app
        self.assertEqual(app.config['WS_URL'], '/testws')

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

    def test_websocket_400(self):
        request = yield from self.client.get('/testws/websocket')
        response = request.response
        self.assertEqual(response.status_code, 400)

    def test_websocket(self):
        websocket = yield from self.ws()
        handler = websocket.handler
        self.assertEqual(len(handler.rpc_methods), 5)
        self.assertTrue(handler.rpc_methods.get('add'))

    def test_add(self):
        websocket = yield from self.ws()
        msg = json.dumps(dict(method='add', params=dict(a=4, b=6)))
        websocket.handler.on_message(websocket, msg)

