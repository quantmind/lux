from pulsar.apps.ws import WebSocket

import lux
from lux import Parameter

from .ws import LuxWs


class Extension(lux.Extension):

    _config = [
        Parameter('WS_URL', '/ws', 'Websocket base url')
    ]

    def middleware(self, app):
        '''Add middleware to edit content
        '''
        cfg = app.config
        self.websocket = LuxWs()
        return [WebSocket(cfg['WS_URL'], self.websocket)]
