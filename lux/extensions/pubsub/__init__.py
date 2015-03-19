from pulsar.apps.ws import WebSocket
from pulsar.apps.data import create_store

import lux
from lux import Parameter

from .ws import LuxWs


class Extension(lux.Extension):

    _config = [
        Parameter('WS_URL', '/ws', 'Websocket base url'),
        Parameter('PUBSUB_STORE', None,
                  'Connection string for a Publish/Subscribe data-store'),
    ]

    def middleware(self, app):
        '''Add middleware to edit content
        '''
        cfg = app.config
        pubsub = None
        pubsub_store = cfg['PUBSUB_STORE']
        if pubsub_store:
            self.pubsub_store = create_store(pubsub_store)
            pubsub = self.pubsub_store.pubsub()
        self.websocket = LuxWs(pubsub=pubsub)
        return [WebSocket(cfg['WS_URL'], self.websocket)]
