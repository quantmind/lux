'''
Websocket handler for SockJS clients.
'''
import lux
from pulsar.apps.data import create_store

from lux import Parameter

from .socketio import SocketIO
from .ws import LuxWs, RpcWsMethod


__all__ = ['RpcWsMethod']


class Extension(lux.Extension):

    _config = [
        Parameter('WS_URL', '/ws', 'Websocket base url'),
        Parameter('WS_HANDLER', LuxWs, 'Websocket handler'),
        Parameter('PUBSUB_STORE', None,
                  'Connection string for a Publish/Subscribe data-store'),
        Parameter('WEBSOCKET_HARTBEAT', 25, 'Hartbeat in seconds'),
        Parameter('WEBSOCKET_AVAILABLE', True,
                  'Server handle websocket'),
    ]

    def on_config(self, app):
        app.add_events(('on_websocket_open', 'on_websocket_close'))

    def middleware(self, app):
        '''Add middleware to edit content
        '''
        app.pubsub_store = None
        if app.config['PUBSUB_STORE']:
            app.pubsub_store = create_store(app.config['PUBSUB_STORE'])
            app.pubsubs = {}
        handler = app.config['WS_HANDLER']
        if handler:
            socketio = SocketIO(app.config['WS_URL'], handler(app))
            return [socketio]
