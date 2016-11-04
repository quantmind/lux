"""Module implementing Lux websocket handler and websocket
remote procedure call framework
"""
import time
import json
import hashlib
import logging

from pulsar import ProtocolError
from pulsar.apps import ws

from .rpc import WsRpc


CONNECTION_ESTABLISHED = 'established'
CONNECTION = 'connection'


class WsClient:
    """Server side of a websocket client.

    Instances of this class are passes around in the same way as the
    WSGI request object is for standard HTTP views

    .. attr: transport

        The websocket protocol with the connection to the client

    .. attr: rpc

        The rpc for handling messanges from the client

    """
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
        self.cache.ws_rpc_methods = {}
        self.rpc = WsRpc(self)

    @property
    def channels(self):
        """handler for publish/subscribe channels
        """
        return self.app.channels

    @property
    def cache(self):
        """A cache object to store session persistent data
        """
        return self.transport.cache

    @property
    def handler(self):
        """Websocket handler
        """
        return self.transport.handler

    @property
    def wsgi_request(self):
        """Original WSGI request which obtained the websocket upgrade
        """
        return self.transport.handshake

    @property
    def protocol(self):
        """Protocol object for encoding/decoding messanges
        """
        return self.app.channels.protocol

    def __str__(self):
        return '%s - %s' % (self.address, self.session_id)

    def write(self, msg):
        array = [self.protocol.encode(msg)]
        self.transport.write('a%s' % json.dumps(array))

    def on_open(self):
        self.transport.on_open(self)
        self.app.fire('on_websocket_open', self)
        self.write_message(CONNECTION,
                           CONNECTION_ESTABLISHED,
                           data=dict(socket_id=self.session_id,
                                     time=self.started))

    async def on_message(self, message):
        """Handle a new message in the websocket
        """
        try:
            # SockJS sends a string as a single element of an array.
            # Therefore JSON is double-encoded!
            msg = json.loads(message)
            if not isinstance(msg, list):
                raise ProtocolError('Malformed message; expected list, '
                                    'got %s' % type(msg).__name__)
            data = self.protocol.decode(msg[0])
            if not isinstance(data, dict):
                raise ProtocolError('Malformed data; expected dict, '
                                    'got %s' % type(data).__name__)
            await self.rpc(data)
        except ProtocolError as exc:
            self.logger.error('Protocol error: %s', str(exc))
        except Exception:
            self.logger.exception('While loading websocket message')
            self.transport.connection.close()

    def on_close(self):
        self.app.fire('on_websocket_close', self)
        self.logger.info('closing socket %s', self)

    def write_message(self, channel, event, data):
        msg = {'event': event, 'channel': channel}
        if data:
            msg['data'] = data
        self.write(msg)


class LuxWs(ws.WS):
    """Lux websocket

    .. attribute: rpc_methods

        Dictionary of RPC web-socket handlers. Each handler is accessed by
        its name defined at extension level as ``ws_<method>``.

    If the application uses greenio concurrency, all websockets callbacks
    (on_open, on_message and on_close) are run in the application
    green pool.
    """
    def __init__(self, app):
        """"Load all websocket RPC methods
        """
        self.rpc_methods = dict(self._ws_methods(app))

    def on_open(self, websocket):
        """When the websocket opens, register a lux client
        """
        websocket.cache.wsclient = WsClient(websocket)
        websocket.cache.wsclient.on_open()

    def on_message(self, websocket, message):
        return websocket.cache.wsclient.on_message(message)

    def on_close(self, websocket):
        websocket.cache.wsclient.on_close()

    def _ws_methods(self, app):
        """Search for web-socket rpc-handlers in all registered extensions.

        A websocket handler is a method prefixed by ``ws_``.
        """
        for ext in app.extensions.values():
            for name in dir(ext):
                if name.startswith('ws_'):
                    handler = getattr(ext, name, None)
                    name = '_'.join(name.split('_')[1:])
                    if hasattr(handler, '__call__'):
                        yield name, handler
