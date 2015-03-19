import time
import json
import hashlib

from pulsar.apps import ws

LUX_CONNECTION = 'lux:connection_established'
LUX_ERROR = 'lux:error'


class WsClient:
    '''Server side of a websocket client
    '''
    def __init__(self, websocket, handler):
        self.websocket = websocket
        self.handler = handler
        self.started = time.time()
        self.address = websocket.handshake.get_client_address()
        self.id = hashlib.sha224(str(self)).hexdigest()
        websocket.handshake.cache.websocket = self

    def __str__(self):
        return '%s - %s' % (self.address, self.started)

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
            msg['data'] = json.dumps(data)
        self.websocket.write(json.dumps(msg))

    def error_message(self, ws, exc):
        msg = {'event': LUX_ERROR}
        code = getattr(exc, 'code', None)
        if code:
            msg['code'] = code
        msg['message'] = str(exc)


class LuxWs(ws.WS):
    '''Lux websocket
    '''
    def __init__(self, pubsub=None):
        self.pubsub = pubsub

    def on_open(self, websocket):
        ws = WsClient(websocket, self)
        if self.pubsub:
            self.pubsub.add(ws)
        #
        # Send the LUX_CONNECTION event with socket id and start time
        ws.write(LUX_CONNECTION, socket_id=ws.id, time=ws.started)

    def on_message(self, websocket, message):
        ws = websocket.handshake.cache.websocket
        try:
            msg = json.loads(message)

        except Exception as exc:
            ws.error_message(exc)
