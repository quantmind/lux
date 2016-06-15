"""Websocket RPC for Authentication"""
from pulsar import Http401, PermissionDenied
from pulsar.apps import rpc

from lux.core import Resource


class WsResource(Resource):

    def __call__(self, request, **kw):
        try:
            return super().__call__(request, **kw)
        except PermissionDenied:
            raise rpc.InvalidRequest('permission denied')


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
        except Http401 as exc:
            raise rpc.InvalidParams('bad authToken') from exc
        args = {model.id_field: getattr(wsgi.cache.user, model.id_field)}
        user = model.get_instance(wsgi, **args)
        user_info = model.tojson(wsgi, user)
        wsrequest.cache.user_info = user_info
        return user_info
