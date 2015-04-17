import lux


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.sockjs']

WS_URL = '/testws'


class Extension(lux.Extension):

    def on_websocket_message(self, ws, msg):
        pass
