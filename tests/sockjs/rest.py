import json
from lux.utils import test

from pulsar import ProtocolError


class TestSockJSRestApp(test.AppTestCase):
    config_file = 'tests.sockjs'
    credentials = dict(username='bigpippo', password='bigpippo')

    @classmethod
    def populatedb(cls):
        backend = cls.app.auth_backend
        backend.create_superuser(cls.app.wsgi_request(),
                                 email='bigpippo@pluto.com',
                                 first_name='Big Pippo',
                                 **cls.credentials)

    def _token(self):
        '''Return a token for a new superuser
        '''

        # Get new token
        request = yield from self.client.post('/authorizations',
                                              content_type='application/json',
                                              body=self.credentials)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())
        data = self.json(request.response, 201)
        self.assertTrue('token' in data)
        return data['token']

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

    def test_websocket_handler(self):
        websocket = yield from self.ws()
        handler = websocket.handler
        self.assertEqual(len(handler.rpc_methods), 5)
        self.assertTrue(handler.rpc_methods.get('add'))

    def test_ws_protocol_error(self):
        websocket = yield from self.ws()
        logger = websocket.cache.wsclient.logger

        msg = json.dumps(dict(method='add', params=dict(a=4, b=6)))
        yield from websocket.handler.on_message(websocket, msg)
        logger.error.assert_called_with(
                'Protocol error: %s',
                'Malformed message; expected list, got dict')
        #
        logger.reset_mock()
        msg = json.dumps(['?'])
        yield from websocket.handler.on_message(websocket, msg)
        logger.error.assert_called_with(
                'Protocol error: %s',
                'Invalid JSON')
        #
        logger.reset_mock()
        msg = json.dumps([json.dumps('?')])
        yield from websocket.handler.on_message(websocket, msg)
        logger.error.assert_called_with(
                'Protocol error: %s',
                'Malformed data; expected dict, got str')

    def test_ws_add_error(self):
        websocket = yield from self.ws()
        msg = self.ws_message(method='add', params=dict(a=4, b=6))
        yield from websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'Request ID not available')

    def test_ws_add(self):
        websocket = yield from self.ws()
        msg = self.ws_message(method='add', params=dict(a=4, b=6), id="57")
        yield from websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['result'], 10)

    def test_ws_authenticate_error(self):
        websocket = yield from self.ws()
        msg = self.ws_message(method='authenticate', id=5)
        yield from websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'authToken missing')
        self.assertEqual(msg['id'], 5)

    def test_ws_authenticate_fails(self):
        websocket = yield from self.ws()
        msg = self.ws_message(method='authenticate', id="dfg",
                              params=dict(authToken='dsd'))
        yield from websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'bad authToken')

    def test_ws_authenticate(self):
        token = yield from self._token()
        websocket = yield from self.ws()
        msg = self.ws_message(method='authenticate', id="dfg",
                              params=dict(authToken=token))
        yield from websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertTrue(msg['result'])
        self.assertEqual(msg['result']['username'], 'bigpippo')

    def test_ws_publish_fails(self):
        websocket = yield from self.ws()
        #
        msg = self.ws_message(method='publish', id=456)
        yield from websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'missing channel')
        #
        msg = self.ws_message(method='publish', id=456,
                              params=dict(channel='foo'))
        yield from websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'missing event')

    def test_ws_publish(self):
        websocket = yield from self.ws()
        #
        msg = self.ws_message(method='publish', id=456,
                              params=dict(channel='foo', event='myevent'))
        yield from websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['result'], 0)
