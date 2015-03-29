'''
Websocket handler for SockJS clients.
'''
import lux
from pulsar.apps.data import create_store

from lux import Parameter

from .socketio import SocketIO
from .ws import LuxWs


class Extension(lux.Extension):

    _config = [
        Parameter('WS_URL', '/ws', 'Websocket base url'),
        Parameter('PUBSUB_STORE', None,
                  'Connection string for a Publish/Subscribe data-store'),
        Parameter('WEBSOCKET_HARTBEAT', 25, 'Hartbeat in seconds'),
        Parameter('WEBSOCKET_AVAILABLE', True,
                  'Server handle websocket'),
    ]

    def on_config(self, app):
        app.add_events(['on_websocket_open'])

    def middleware(self, app):
        '''Add middleware to edit content
        '''
        socketio = SocketIO(app.config['WS_URL'])
        self.websocket = socketio.handle
        return [socketio]

    def on_loaded(self, app):
        pubsub_store = app.config['PUBSUB_STORE']
        if pubsub_store:
            self.pubsub_store = create_store(pubsub_store)
            self.websocket.pubsub = self.pubsub_store.pubsub()
