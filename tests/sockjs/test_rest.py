import json
import asyncio

from lux.utils import test


class TestSockJSRestApp(test.AppTestCase):
    config_file = 'tests.sockjs'

    async def ws(self):
        request = await self.client.wsget('/testws/websocket')
        return self.ws_upgrade(request.response)

    def test_app(self):
        app = self.app
        self.assertEqual(app.config['WS_URL'], '/testws')

    async def test_get(self):
        request = await self.client.get('/testws')
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type,
                         'text/plain; charset=utf-8')

    async def test_info(self):
        request = await self.client.get('/testws/info')
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type,
                         'application/json; charset=utf-8')

    async def test_websocket_400(self):
        request = await self.client.get('/testws/websocket')
        response = request.response
        self.assertEqual(response.status_code, 400)

    async def test_websocket_handler(self):
        websocket = await self.ws()
        handler = websocket.handler
        self.assertEqual(len(handler.rpc_methods), 8)
        self.assertTrue(handler.rpc_methods.get('add'))

    async def test_ws_protocol_error(self):
        websocket = await self.ws()
        logger = websocket.cache.wsclient.logger

        msg = json.dumps(dict(method='add', params=dict(a=4, b=6)))
        await websocket.handler.on_message(websocket, msg)
        logger.error.assert_called_with(
            'Protocol error: %s',
            'Malformed message; expected list, got dict')
        #
        logger.reset_mock()
        msg = json.dumps(['?'])
        await websocket.handler.on_message(websocket, msg)
        logger.error.assert_called_with(
            'Protocol error: %s',
            'Invalid JSON')
        #
        logger.reset_mock()
        msg = json.dumps([json.dumps('?')])
        await websocket.handler.on_message(websocket, msg)
        logger.error.assert_called_with(
            'Protocol error: %s',
            'Malformed data; expected dict, got str')

    async def test_ws_add_error(self):
        websocket = await self.ws()
        msg = self.ws_message(method='add', params=dict(a=4, b=6))
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'Request ID not available')

    async def test_ws_add(self):
        websocket = await self.ws()
        msg = self.ws_message(method='add', params=dict(a=4, b=6), id="57")
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['result'], 10)

    async def test_ws_authenticate_error(self):
        websocket = await self.ws()
        msg = self.ws_message(method='authenticate', id=5)
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'missing authToken')
        self.assertEqual(msg['id'], 5)

    async def test_ws_authenticate_fails(self):
        websocket = await self.ws()
        msg = self.ws_message(method='authenticate', id="dfg",
                              params=dict(authToken='dsd'))
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'bad authToken')

    async def test_ws_authenticate(self):
        token = await self._token('testuser')
        websocket = await self.ws()
        msg = self.ws_message(method='authenticate', id="dfg",
                              params=dict(authToken=token))
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertTrue(msg['result'])
        self.assertEqual(msg['result']['username'], 'testuser')
        return websocket

    async def test_ws_publish_fails(self):
        websocket = await self.ws()
        #
        msg = self.ws_message(method='publish', id=456)
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'missing channel')
        #
        msg = self.ws_message(method='publish', id=456,
                              params=dict(channel='foo'))
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'missing event')

    async def test_ws_publish(self):
        websocket = await self.ws()
        #
        msg = self.ws_message(method='publish', id=456,
                              params=dict(channel='foo', event='myevent'))
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertTrue('result' in msg)

    async def test_ws_subscribe_fails(self):
        websocket = await self.ws()
        #
        msg = self.ws_message(method='subscribe', id=456)
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'missing channel')
        #
        msg = self.ws_message(method='subscribe', id=456,
                              params=dict(channel='foo'))
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'missing event')

    async def test_ws_subscribe(self):
        websocket = await self.ws()
        #
        msg = self.ws_message(method='subscribe', id=456,
                              params=dict(channel='pizza', event='myevent'))
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertTrue('lux-pizza' in msg['result'])
        #
        msg = self.ws_message(method='subscribe', id=4556,
                              params=dict(channel='lux-foo', event='myevent'))
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertTrue('lux-pizza' in msg['result'])
        self.assertTrue('lux-foo' in msg['result'])

    async def test_ws_model_metadata_fails(self):
        websocket = await self.ws()
        #
        msg = self.ws_message(method='model_metadata', id=456)
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'missing model')
        #
        msg = self.ws_message(method='model_metadata', id=456,
                              params=dict(model='foo'))
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertEqual(msg['error']['message'], 'Model "foo" does not exist')

    async def test_ws_model_metadata(self):
        websocket = await self.ws()
        #
        msg = self.ws_message(method='model_metadata', id=456,
                              params=dict(model='user'))
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        self.assertTrue(msg['result'])
        self.assertTrue(msg['result']['columns'])
        self.assertTrue(msg['result']['permissions'])

    async def test_ws_model_data(self):
        websocket = await self.ws()
        #
        msg = self.ws_message(method='model_data', id=456,
                              params=dict(model='user'))
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        data = msg['result']
        self.assertTrue(data)
        self.assertTrue(data['total'])
        self.assertTrue(data['result'])

    async def test_model_create(self):
        #
        # Subscribe to create event
        ws = await self.ws()
        msg = self.ws_message(method='subscribe', id=456,
                              params=dict(channel='lux-tasks',
                                          event='create'))
        await ws.handler.on_message(ws, msg)
        msg = self.get_ws_message(ws)
        self.assertTrue('lux-tasks' in msg['result'])
        future = asyncio.Future()
        ws.connection.write = future.set_result
        #
        websocket = await self.test_ws_authenticate()
        msg = self.ws_message(method='model_create', id=456,
                              params=dict(model='tasks',
                                          subject='just a test'))
        await websocket.handler.on_message(websocket, msg)
        msg = self.get_ws_message(websocket)
        data = msg['result']
        self.assertTrue(data)
        self.assertEqual(data['subject'], 'just a test')
        #
        frame = await asyncio.wait_for(future, 1.5)
        ws.connection.reset_mock()
        self.assertTrue(frame)
        msg = self.parse_frame(ws, frame)
        self.assertTrue(msg)
        self.assertEqual(msg['event'], 'create')
        self.assertEqual(msg['channel'], 'lux-tasks')
        self.assertEqual(msg['data'], data)
