import lux

from pulsar.apps.ws import WebSocket

from .ws import LuxWs


class Extension(lux.Extension):
    '''This extension should be the last extension which provides
    a middleware serving urls.'''

    _config = [
        Parameter('WS_URL', '/ws', 'Websocket base url')
    ]

    def middleware(self, app):
        '''Add middleware to edit content
        '''
        cfg = app.config
        app.websocket = LuxWs()
        return [WebSocket(cfg['WS_URL'], app.websocket)]
