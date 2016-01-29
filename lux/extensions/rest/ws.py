"""Websocket RPC method for authenticating a user
"""
from pulsar.apps import rpc

from lux import Http401
from lux.extensions.sockjs import RpcWsMethod


class WsAuthentication(RpcWsMethod):
    """Websocket authentication using a token

    The client should send the following rpc request at the beginning of the
    session:

        rpc('authenticate', {'token': ...})

    The rpc call will return an exception or an object with user data
    """
    user_info = None

    def on_request(self, request):
        self.check_user()
        token = request.data.get("token")
        if not token:
            raise rpc.InvalidParams('token missing')
        wsgi_request = self.ws.wsgi_request
        backend = wsgi_request.backend
        auth = 'bearer %s' % token
        try:
            backend.authorize(auth)
        except Http401:
            raise rpc.InvalidParams('token')
        self.cache.user_info = self.user_info()
        request.send_response(data=self.cache.user_info)

    def check_user(self):
        if self.cache.user_info:
            raise rpc.InvalidRequest('Already authenticated')

    def user_info(self):
        wsgi_request = self.ws.wsgi_request
        model = self.ws.app.models['user']
        self.user_info = model.serialize(wsgi_request, self.cache.user)
