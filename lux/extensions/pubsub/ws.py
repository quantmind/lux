import time
import json
import hashlib

from pulsar.apps import ws

LUX_CONNECTION = 'lux:connection_established'


class WsClient:

    def __init__(self, websocket, handler):
        self.websocket = websocket
        self.handler = handler
        self.started = time.time()
        self.address = websocket.handshake.get_client_address()
        self.id = hashlib.sha224(str(self)).hexdigest()
        websocket.handshake.cache.websocket = self

    def __str__(self):
        return '%s - %s' % (self.address, self.started)


class LuxWs(ws.WS):
    '''Lux websocket
    '''
    def __init__(self, pubsub=None):
        self.pubsub = pubsub

    def on_open(self, websocket):
        ws = WsClient(websocket, self)
        if self.pubsub:
            self.pubsub.add(ws)
        self.execute(websocket, LUX_CONNECTION,
                     socket_id=ws.id, time=ws.started)

    def execute(websocket, event, channel=None, data=None, **kw):
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
        self.write(json.dumps(msg))

