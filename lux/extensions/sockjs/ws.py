import time
import json
import hashlib
import logging
from inspect import isclass

from pulsar.apps import ws, rpc
from pulsar import maybe_async

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

    @property
    def cache(self):
        '''A cache object to store session persistent data
        '''
        return self.transport.cache

    @property
    def rpc_methods(self):
        '''A cache object to store session persistent data
        '''
        return self.transport.handler.rpc_methods

    def __str__(self):
        return '%s - %s' % (self.address, self.session_id)

    def on_open(self):
        self.transport.on_open(self)
        self.app.fire('on_websocket_open', self)
        self.write(LUX_CONNECTION,
                   socket_id=self.session_id,
                   time=self.started)

    def on_message(self, message):
        try:
            data = self._load(message)
            self._response(data)
        except Exception as exc:
            self.logger.exception('While loading websocket message')
            self.error_message(exc)
            self.transport.connection.close()

    def on_close(self):
        self.app.fire('on_websocket_close', self)
        self.logger.info('closing socket %s', self)

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

    # INTERNALS
    def _load(self, message):
        # SockJS sends a string as a single element of an array.
        # Therefore JSON is double-encoded!
        msg = json.loads(message)
        if not isinstance(msg, list):
            raise ValueError('Malformed message; expected array')
        data = json.loads(msg[0])
        if not isinstance(data, dict):
            raise ValueError('Expected data dictionary')
        return data

    def _response(self, msg):
        if 'method' in msg:
            method = msg['method']
            handler = self.rpc_methods.get(method)
            if not handler:
                raise rpc.NoSuchFunction(method)
            handler(self, msg.get('id'), msg.get('data'))
        else:
            raise rpc.InvalidRequest


class RpcWsMethodResponder:
    """Used to respond to RPC requests"""
    def __init__(self, method, request_id):
        """
        Initialises the responder

        :param method:          RpcWsMethod object
        :param request_id:      RPC request ID
        """
        self.method = method
        self.request_id = request_id

    def send_response(self, data, rpc_complete=True,
                      message_type=LUX_MESSAGE):
        """
        Sends a response to the client

        :param data:            data to send
        :param rpc_complete:    True if this is the last message being sent
                                in response to the message received
        :param message_type:    LUX_MESSAGE or LUX_ERROR
        :return:
        """
        response = {
            'method': self.method.name,
            'id': self.request_id,
            'rpcComplete': rpc_complete,
            'data': data
        }
        self.method.ws.write(message_type, 'rpc', response)

    def send_error(self, data, rpc_complete=True):
        """Calls send_response with message_type=LUX_ERROR"""
        self.send_response(data, rpc_complete, LUX_ERROR)


class RpcWsMethod:

    def __init__(self, name, ws):
        self.name = name
        self.ws = ws
        maybe_async(self.on_init())

    @property
    def app(self):
        return self.ws.app

    def on_init(self):
        '''Called the first time this method is invoked within a given
        websocket connection.

        It can returns an asynchronous component
        '''
        pass

    def handle_request(self, request_id, data):
        self.on_request(RpcWsMethodResponder(self, request_id), data)

    def on_request(self, responder, data):
        """
        To be overridden by subclasses

        :param responder:    RpcWsMethodResponder instance
        :param data:         data send by client
        """
        pass

    def pubsub(self, key=None):
        '''Convenience method for a pubsub handler
        '''
        return self.app.pubsub(key or self.name)


class RpcWsCall:
    '''A wrapper for a :class:`.RpcWsMethod`
    '''
    def __init__(self, method, rpc):
        self.method = method
        self.rpc = rpc

    def __repr__(self):
        return self.method

    def __call__(self, ws, id, data):
        if self.method not in ws.cache:
            ws.cache[self.method] = self.rpc(self.method, ws)
        ws.cache[self.method].handle_request(id, data)


class LuxWs(ws.WS):
    '''Lux websocket

    .. attribute: methods

        Dictionary of RPC web-socket handlers. Each handler is accessed by
        its name defined at extension level as ``ws_<method>``.

    '''
    def __init__(self, app):
        self.rpc_methods = dict(self._ws_methods(app))

    def on_open(self, websocket):
        '''When the websocket opens, register a lux client
        '''
        websocket.cache.wsclient = WsClient(websocket)
        return self._green(websocket.app, websocket.cache.wsclient.on_open)

    def on_message(self, websocket, message):
        return self._green(websocket.app, websocket.cache.wsclient.on_message,
                           message)

    def on_close(self, websocket):
        return self._green(websocket.app, websocket.cache.wsclient.on_close)

    def _green(self, app, callable, *args, **kwargs):
        if app.green_pool:
            return app.green_pool.submit(callable, *args, **kwargs)
        else:
            return callable()

    def _ws_methods(self, app):
        '''Search for web-socket rpc-handlers in all registered extensions.

        A websocket handler is a method prefixed by ``ws_``.
        '''
        for ext in app.extensions.values():
            for name in dir(ext):
                if name.startswith('ws_'):
                    handler = getattr(ext, name, None)
                    name = '_'.join(name.split('_')[1:])
                    if isclass(handler) and issubclass(handler, RpcWsMethod):
                        handler = RpcWsCall(name, handler)
                    if hasattr(handler, '__call__'):
                        yield name, handler
