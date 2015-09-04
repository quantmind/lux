import time
import json
import hashlib
import logging

from pulsar.apps import ws
from builtins import isinstance

LUX_CONNECTION = 'lux:connection_established'
LUX_MESSAGE = 'lux:message'
LUX_ERROR = 'lux:error'


class WsClient:
    '''Server side of a websocket client.

    .. attr: transport

        The websocket protocol with the connection to the client

    '''
    logger = logging.getLogger('lux.sockjs')

    def __init__(self, transport):
        request = transport.handshake
        self.transport = transport
        self.app = request.app
        self.started = time.time()
        self.address = request.get_client_address()
        session_id = request.urlargs.get('session_id')
        if not session_id:
            key = '%s - %s' % (self.address, self.started)
            session_id = hashlib.sha224(key.encode('utf-8')).hexdigest()
        self.session_id = session_id
        transport.cache.wsclient = self
        transport.on_open(self)

    def __str__(self):
        return '%s - %s' % (self.address, self.session_id)

    def __call__(self, channel, message):
        '''Invoked by the pubsub handler when a new message on a channel
        is available.'''
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

    def error_message(self, exc, code=None):
        '''Write an error message back to the client
        '''
        data = {}
        code = getattr(exc, 'fault_code', code)
        if code:
            data['code'] = code
        data['message'] = str(exc)
        self.write(LUX_ERROR, data=data)


class LuxWs(ws.WS):
    '''Lux websocket
    '''
    pubsub = None
    '''Publish/subscribe handler'''

    def on_open(self, websocket):
        ws = WsClient(websocket)
        websocket.app.fire('on_websocket_open', ws)
        #
        # Send the LUX_CONNECTION event with socket id and start time
        ws.write(LUX_CONNECTION, socket_id=ws.session_id, time=ws.started)

    def on_message(self, websocket, message):
        '''When a new message arrives, decode it into json
        and fire the ``on_websocket_message`` event.
        '''
        ws = websocket.cache.wsclient
        try:
            # SockJS sends a string as a single element of an array.
            # Therefore JSON is double-encoded!
            msg = json.loads(message)
            if not isinstance(msg, list):
                raise ValueError('Malformed message; expected array')
            msg = json.loads(msg[0])
        except Exception as exc:
            ws.error_message(exc)
        else:
            websocket.app.fire('on_websocket_message', ws, msg)

    def on_close(self, websocket):
        ws = websocket.cache.wsclient
        if self.pubsub:
            self.pubsub.remove_client(ws)
        websocket.app.fire('on_websocket_close', ws)
        ws.logger.info('closing socket %s', ws)
