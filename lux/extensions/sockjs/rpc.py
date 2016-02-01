from pulsar.apps import rpc

from lux import Http401
from lux.utils.async import maybe_green


rpc_version = '1.0'


class WsRpc:
    """RPC handler for websockets
    """
    __slots__ = ('ws',)

    def __init__(self, ws):
        self.ws = ws

    @property
    def methods(self):
        """A cache object to store session persistent data
        """
        return self.ws.handler.rpc_methods

    def write(self, request_id, result=None, error=None):
        """Write a response to an RPC message
        """
        response = {'id': request_id,
                    'version': rpc_version}
        if result is not None:
            response['result'] = result
        if error:
            assert 'result' not in response, 'result and error not possible'
            response['error'] = error
        else:
            assert 'result' in response, 'error or result must be given'
        self.ws.write(response)

    def write_error(self, request_id, message, code=None, data=None):
        if code is None:
            code = getattr(message, 'fault_code', rpc.InternalError.fault_code)
        error = dict(message=str(message), code=code)
        if data:
            error['data'] = data
        self.write(request_id, error=error)

    def __call__(self, data):
        request_id = data.get('id')
        try:
            if 'method' in data:
                if not request_id:
                    raise rpc.InvalidRequest('Request ID not available')
                method = data['method']
                handler = self.methods.get(method)
                if not handler:
                    raise rpc.NoSuchFunction(method)
                #
                request = RpcWsMethodRequest(self, request_id,
                                             data.get('params'))
                result = yield from maybe_green(self.ws.app, handler, request)
                self.write(request_id, result)
            else:
                raise rpc.InvalidRequest('Method not available')
        except rpc.InvalidRequest as exc:
            self.write_error(request_id, exc)
        except Exception as exc:
            self.ws.logger.exception('While loading websocket message')
            self.write_error(request_id, exc)


class RpcWsMethodRequest:
    """Internal class for responding to RPC requests
    """
    __slots__ = ('rpc', 'id', 'params')

    def __init__(self, rpc, request_id, params):
        """
        Initialises the responder

        :param id:      RPC request ID
        :param params:  RPC parameters
        """
        self.rpc = rpc
        self.id = request_id
        self.params = params if params is not None else {}
        if not isinstance(self.params, dict):
            raise rpc.InvalidRequest('params entry must be a dictionary')

    @property
    def ws(self):
        return self.rpc.ws

    @property
    def logger(self):
        return self.ws.logger

    @property
    def cache(self):
        return self.ws.cache


class WsAuthentication:

    def ws_authenticate(self, request):
        """Websocket RPC method for authenticating a user
        """
        if request.cache.user_info:
            raise rpc.InvalidRequest('Already authenticated')
        token = request.params.get("authToken")
        if not token:
            raise rpc.InvalidParams('authToken missing')
        model = request.ws.app.models.get('user')
        if not model:
            raise rpc.InternalError('user model missing')
        wsgi = request.ws.wsgi_request
        backend = wsgi.cache.auth_backend
        auth = 'bearer %s' % token
        try:
            backend.authorize(wsgi, auth)
        except Http401 as exc:
            raise rpc.InvalidParams('bad authToken') from exc
        user_info = model.serialise(wsgi, wsgi.cache.user)
        request.cache.user_info = user_info
        return user_info
