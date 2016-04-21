"""
Websocket handler for SockJS clients.
"""
from lux.core import Parameter, LuxExtension

from .socketio import SocketIO
from .ws import LuxWs
from .auth import WsModelRpc, check_ws_permission, get_model
from .pubsub import PubSub, Channels, broadcast


__all__ = ['Channels',
           'broadcast',
           'check_ws_permission',
           'get_model']


class Extension(LuxExtension, PubSub, WsModelRpc):

    _config = [
        Parameter('WS_URL', '/ws', 'Websocket base url'),
        Parameter('WS_HANDLER', LuxWs, 'Websocket handler'),
        Parameter('WEBSOCKET_HARTBEAT', 25, 'Hartbeat in seconds'),
        Parameter('WEBSOCKET_AVAILABLE', True,
                  'Server handle websocket')
    ]

    def on_config(self, app):
        app.add_events(('on_websocket_open', 'on_websocket_close'))

    def middleware(self, app):
        """Add middleware to edit content
        """
        handler = app.config['WS_HANDLER']
        url = app.config['WS_URL']
        if handler and url:
            return [SocketIO(url, handler(app))]
