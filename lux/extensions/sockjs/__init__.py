"""
Websocket handler for SockJS clients.
"""
from lux.core import Parameter, LuxExtension
from pulsar.utils.importer import module_attribute

from .socketio import SocketIO
from .ws import LuxWs
from . import rpc


__all__ = ['LuxWs']


class Extension(LuxExtension,
                rpc.WsChannelsRpc,
                rpc.WsAuthRpc,
                rpc.WsModelRpc):

    _config = [
        Parameter('WS_URL', '/ws', 'Websocket base url'),
        Parameter('WS_HANDLER', 'lux.extensions.sockjs:LuxWs',
                  'Dotted path to websocket handler'),
        Parameter('WEBSOCKET_HARTBEAT', 25, 'Hartbeat in seconds'),
        Parameter('WEBSOCKET_AVAILABLE', True,
                  'websocket server handle available')
    ]

    def on_config(self, app):
        app.add_events(('on_websocket_open', 'on_websocket_close'))

    def middleware(self, app):
        """Add websocket middleware
        """
        url = app.config['WS_URL']
        if url:
            handler = module_attribute(app.config['WS_HANDLER'])
            return [SocketIO(url, handler(app))]
