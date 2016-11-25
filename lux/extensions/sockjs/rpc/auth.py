"""Websocket RPC for Authentication"""
from pulsar import PermissionDenied, BadRequest, Http401
from pulsar.apps import rpc

from lux.core import Resource


class WsResource(Resource):

    def __call__(self, request, **kw):
        try:
            return super().__call__(request, **kw)
        except PermissionDenied:
            raise rpc.InvalidRequest('permission denied') from None
        except Http401:
            raise rpc.InvalidRequest('authentication required') from None


class WsAuthRpc:

    def ws_authenticate(self, wsrequest):
        """Websocket RPC method for authenticating a user
        """
        if wsrequest.cache.user_info:
            raise rpc.InvalidRequest('Already authenticated')
        token = wsrequest.required_param("authToken")
        model = wsrequest.app.models.get('user')
        if not model:
            raise rpc.InternalError('user model missing')
        wsgi = wsrequest.ws.wsgi_request
        backend = wsgi.cache.auth_backend
        auth = 'bearer %s' % token
        try:
            backend.authorize(wsgi, auth)
        except BadRequest:
            raise rpc.InvalidParams('bad authToken') from None
        args = {model.id_field: getattr(wsgi.cache.user, model.id_field)}
        user = model.get_instance(wsgi, **args)
        user_info = model.tojson(wsgi, user)
        wsrequest.cache.user_info = user_info
        return user_info
