import time
import json
import hashlib
import logging

from pulsar.apps import ws
from builtins import isinstance

LUX_CONNECTION = 'lux:connection_established'
LUX_MESSAGE = 'lux:message'
LUX_ERROR = 'lux:error'

LOGGER = logging.getLogger('lux.sockjs')


class WsClient:
    '''Server side of a websocket client
    '''
    def __init__(self, transport, handler):
        request = transport.handshake
        self.transport = transport
        self.handler = handler
        self.started = time.time()
        self.address = request.get_client_address()
        session_id = request.urlargs.get('session_id')
        if not session_id:
            key = '%s - %s' % (self.address, self.started)
            session_id = hashlib.sha224(key.encode('utf-8')).hexdigest()
        self.session_id = session_id
        request.cache.websocket = self
        transport.on_open(self)

    def __str__(self):
        return '%s - %s' % (self.address, self.session_id)

    def __call__(self, channel, message):
        message = message.decode('utf-8')
        self.write(LUX_MESSAGE, channel, message)

    # Lux Implementation
    def write(self, event, channel=None, data=None, **kw):
        msg = {'event': event}
        if channel:
            msg['channel'] = channel
        if kw:
            if data:
                data.update(kw)
            else:
                data = kw
        if data:
            if not isinstance(data, str):
                data = json.dumps(data)
            msg['data'] = data
        array = [json.dumps(msg)]
        self.transport.write('a%s' % json.dumps(array))

    def error_message(self, ws, exc):
        msg = {'event': LUX_ERROR}
        code = getattr(exc, 'code', None)
        if code:
            msg['code'] = code
        msg['message'] = str(exc)


class LuxWs(ws.WS):
    '''Lux websocket
    '''
    pubsub = None

    def on_open(self, websocket):
        ws = WsClient(websocket, self)
        if self.pubsub:
            self.pubsub.add_client(ws)
            app = websocket.app
            app.fire('on_websocket_open', websocket, self)
        #
        # Send the LUX_CONNECTION event with socket id and start time
        ws.write(LUX_CONNECTION, socket_id=ws.session_id, time=ws.started)

    def on_message(self, websocket, message):
        ws = websocket.handshake.cache.websocket
        try:
            msg = json.loads(message)

        except Exception as exc:
            ws.error_message(exc)

    def on_close(self, websocket):
        ws = websocket.handshake.cache.websocket
        if self.pubsub:
            self.pubsub.remove_client(ws)
        LOGGER.info('closing socket %s', ws)
