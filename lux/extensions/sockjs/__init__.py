"""
Websocket handler for SockJS clients.
"""
import json

import lux

from lux import Parameter

from .socketio import SocketIO
from .ws import LuxWs
from .pubsub import PubSub
from .rpc import WsAuthentication


class Extension(lux.Extension, PubSub, WsAuthentication):

    _config = [
        Parameter('WS_URL', '/ws', 'Websocket base url'),
        Parameter('WS_HANDLER', LuxWs, 'Websocket handler'),
        Parameter('WEBSOCKET_HARTBEAT', 25, 'Hartbeat in seconds'),
        Parameter('WEBSOCKET_AVAILABLE', True,
                  'Server handle websocket'),
        Parameter('WEBSOCKET_PROTOCOL', 'lux.extensions.sockjs.Json',
                  'Encoder and decoder for websocket messages. '
                  'Default is json.')
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


class Json:

    def __init__(self, ws):
        self.ws = ws

    def encode(self, msg):
        return json.dumps(msg)

    def decode(self, msg):
        return json.loads(msg)
