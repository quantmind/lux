from pulsar.apps import rpc

from lux.utils.async import maybe_green

from .auth import WsAuthRpc, WsResource
from .channels import WsChannelsRpc
from .model import WsModelRpc

__all__ = ['WsRpc',
           'WsAuthRpc',
           'WsChannelsRpc',
           'WsModelRpc']


rpc_version = '1.0'


class WsRpc:
    """RPC handler for websockets
    """
    __slots__ = ('ws',)

    def __init__(self, ws):
        self.ws = ws

    @property
    def methods(self):
        """Mapping of rpc method names to rpc methods
        """
        return self.ws.handler.rpc_methods

    def write(self, request_id, result=None, error=None):
        """Write a response to an RPC message
        """
        response = {'id': request_id,
                    'version': rpc_version}
        if error:
            assert result is None, 'result and error not possible'
            response['error'] = error
        else:
            response['result'] = result
        self.ws.write(response)

    def write_error(self, request_id, message, code=None, data=None):
        if code is None:
            code = getattr(message, 'fault_code', rpc.InternalError.fault_code)
        if data is None:
            data = getattr(message, 'data', None)
        error = dict(message=str(message), code=code)
        if data:
            error['data'] = data
        self.write(request_id, error=error)

    async def __call__(self, data):
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
                result = await maybe_green(self.ws.app, handler, request)
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
    def app(self):
        return self.ws.app

    @property
    def cache(self):
        return self.ws.cache

    @property
    def wsgi_request(self):
        return self.ws.wsgi_request

    def required_param(self, name):
        """Retrieve a parameter by name

        :param name: the parameter name
        :return: the parameter value or raise ``InvalidParams`` if missing
        """
        value = self.params.get(name)
        if not value:
            raise rpc.InvalidParams('missing %s' % name)
        return value

    def pop_param(self, name, *default):
        """Pop a parameter by name

        :param name: the parameter name
        :return: the parameter value or raise ``InvalidParams`` if missing
            and no default given
        """
        try:
            return self.params.pop(name, *default)
        except KeyError:
            raise rpc.InvalidParams('missing %s' % name) from None

    def resource(self, resource, action, *args):
        return WsResource(resource, action, *args)

    def check_permission(self, resource, action, *args, **kwargs):
        resource = self.resource(resource, action, *args)
        return resource(self.wsgi_request, **kwargs)
