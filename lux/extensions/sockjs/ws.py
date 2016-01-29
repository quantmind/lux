"""Module implementing Lux websocket handler and websocket
remote procedure call framework
"""
import time
import json
import hashlib
import logging
from inspect import isclass

from pulsar import is_async, ensure_future
from pulsar.apps import ws, rpc

LUX_CONNECTION = 'connection_established'
LUX_MESSAGE = 'message'
LUX_ERROR = 'error'
LUX_RPC_CHANNEL = 'rpc'


class WsClient:
    """Server side of a websocket client.

    Instances of this class are passes around in the same way as the
    WSGI request object is for standard HTTP views

    .. attr: transport

        The websocket protocol with the connection to the client

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
    def rpc_methods(self):
        """A cache object to store session persistent data
        """
        return self.handler.rpc_methods

    def __str__(self):
        return '%s - %s' % (self.address, self.session_id)

    def on_open(self):
        self.transport.on_open(self)
        self.app.fire('on_websocket_open', self)
        self.write(LUX_CONNECTION,
                   socket_id=self.session_id,
                   time=self.started)

    def on_message(self, message):
        """Handle a new message in the websocket
        """
        request_id = None
        try:
            msg = self._load(message)
            request_id = msg.get('id')
            if 'method' in msg:
                method = msg['method']
                handler = self.rpc_methods.get(method)
                if not handler:
                    raise rpc.NoSuchFunction(method)
                handler(self, request_id, msg.get('data'))
            else:
                raise rpc.InvalidRequest('Method not available')
        except rpc.InvalidRequest as exc:
            self.error_message(exc, request_id=request_id)
        except Exception as exc:
            self.logger.exception('While loading websocket message')
            self.error_message(exc, request_id=request_id)
            self.transport.connection.close()

    def on_close(self):
        self.app.fire('on_websocket_close', self)
        self.logger.info('closing socket %s', self)

    def pubsub(self, key=None):
        """Convenience method for a pubsub handler
        """
        return self.app.pubsub(key)

    def write_rpc(self, request_id, method=None, channel=None,
                  rpc_complete=True, data=None, json_encoder=None,
                  message_type=None, code=None):
        """Write a response to an RPC message
        """
        message_type = message_type or LUX_MESSAGE
        channel = channel or LUX_RPC_CHANNEL
        response = {'id': request_id,
                    'rpcComplete': rpc_complete}
        if method:
            response['method'] = method
        if data:
            response['data'] = data
        if code:
            response['code'] = code
        if json_encoder:
            response = json_encoder(response)
        self.write(message_type, channel, response)

    def error_rpc(self, request_id, message_type=None, **kw):
        message_type = message_type or LUX_ERROR
        self.write_rpc(request_id, message_type=message_type, **kw)

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
        try:
            self.transport.write('a%s' % json.dumps(array))
        except RuntimeError:
            # TODO: is this the best way to avoid spamming exception
            #       when the websocket is closed by the client?
            pass

    def error_message(self, exc, code=None, request_id=None):
        """Write an error message back to the client
        """
        code = getattr(exc, 'fault_code', code)
        data = str(exc)
        self.error_rpc(request_id, code=code, data=data)

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
    """Internal class for responding to RPC requests
    """
    def __init__(self, method, request_id, data):
        """
        Initialises the responder

        :param method:          RpcWsMethod object
        :param request_id:      RPC request ID
        """
        self.method = method
        self.id = request_id
        self.data = data

    def send_response(self, **kw):
        """
        Sends a response to the client

        Inputs are the same as :meth:`~WsClient.write_rpc` method
        """
        method = self.method
        kw['method'] = method.name
        method.ws.write_rpc(self.id, **kw)

    def send_error(self, **kw):
        """Calls send_response with message_type=LUX_ERROR
        """
        method = self.method
        kw['method'] = method.name
        method.ws.error_rpc(self.id, **kw)


class RpcWsMethod:

    def __init__(self, name, ws):
        self.name = name
        self.ws = ws
        self.first = True

    @property
    def app(self):
        return self.ws.app

    @property
    def cache(self):
        return self.ws.cache

    def on_init(self, request):
        """Called the first time this method is invoked within a given
        websocket connection.

        It can return an asynchronous component
        """
        pass

    def on_request(self, request):
        """
        To be overridden by subclasses

        :param responder:    RpcWsMethodResponder instance
        :param data:         data send by client
        """
        pass

    def pubsub(self, ws, key=None):
        """Convenience method for a pubsub handler
        """
        return ws.app.pubsub(key or self.name)


class RpcWsCall:
    """A wrapper for a :class:`.RpcWsMethod`

    Instances of this class are called at every rpc request

    .. attribute:: method

        The name of rpc method (obtained from lux :class:`.Extension
        ws_<method> methods or :class:`RpcWsMethod` classes)

    .. attribute:: rpc

        The callable handling rpc requests
    """
    def __init__(self, method, rpc):
        self.method = method
        self.rpc = rpc

    def __repr__(self):
        return self.method
    __str__ = __repr__

    def __call__(self, ws, request_id, data):
        """Called by :meth:`.WsClient.on_message` method

        :param ws: the :class:`.WsClient` invoking this response
        :param id: the rpc id which identify this request
        :param data: data sent from the client
        """
        pool = ws.app.green_pool
        rpc_handle = ws.cache.ws_rpc_methods[self.method]
        request = RpcWsMethodResponder(ws, request_id, data)
        if rpc is None:
            # if the rpc method is not in cache create a new one
            rpc_handle = self.rpc(self.method, ws)
            ws.cache.ws_rpc_methods[self.method] = rpc_handle
        if pool:
            if request.first:
                pool.wait(rpc_handle.on_init(request), True)
            pool.wait(rpc_handle.on_request(request), True)
            request.first = False
        else:
            ensure_future(_async_call(rpc_handle, request))


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
        self.rpc_methods = dict(self._ws_methods(app))

    def on_open(self, websocket):
        """When the websocket opens, register a lux client
        """
        websocket.cache.wsclient = WsClient(websocket)
        return _green(websocket.app, websocket.cache.wsclient.on_open)

    def on_message(self, websocket, message):
        return _green(websocket.app, websocket.cache.wsclient.on_message,
                      message)

    def on_close(self, websocket):
        return _green(websocket.app, websocket.cache.wsclient.on_close)

    def _ws_methods(self, app):
        """Search for web-socket rpc-handlers in all registered extensions.

        A websocket handler is a method prefixed by ``ws_``.
        """
        for ext in app.extensions.values():
            for name in dir(ext):
                if name.startswith('ws_'):
                    handler = getattr(ext, name, None)
                    name = '_'.join(name.split('_')[1:])
                    if isclass(handler) and issubclass(handler, RpcWsMethod):
                        handler = RpcWsCall(name, handler)
                    if hasattr(handler, '__call__'):
                        yield name, handler


def _green(app, callable, *args, **kwargs):
    if app.green_pool:
        return app.green_pool.submit(callable, *args, **kwargs)
    else:
        return callable()


def _async_call(rpc_handle, request):
    if request.first:
        result = rpc_handle.on_init(request)
        if is_async(result):
            yield from result
    result = rpc_handle.on_request(request)
    if is_async(result):
        yield from result
    request.first = False
