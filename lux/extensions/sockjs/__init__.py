'''
Websocket handler for SockJS clients.
'''
import lux
from pulsar.apps.data import create_store
from pulsar.apps import rpc

from lux import Parameter

from .socketio import SocketIO
from .ws import LuxWs


__all__ = ['LuxWs', 'SocketIO']


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
        app.add_events(('on_websocket_open',
                        'on_websocket_message',
                        'on_websocket_close'))

    def middleware(self, app):
        '''Add middleware to edit content
        '''
        socketio = SocketIO(app.config['WS_URL'])
        self.websocket = socketio.handle
        return [socketio]

    def on_loaded(self, app):
        '''Once the application has loaded, create the pub/sub
        handler used to publish messages to channels as
        well as subscribe to channels
        '''
        pubsub_store = app.config['PUBSUB_STORE']
        if pubsub_store:
            self.pubsub_store = create_store(pubsub_store)
            self.websocket.pubsub = self.pubsub_store.pubsub()


class WsApi:
    '''Web socket API handler
    '''
    def __init__(self, app):
        self.methods = dict(self._ws_methods(app))

    def __call__(self, ws, msg):
        try:
            if 'method' in msg:
                method = msg['method']
                if method in self.ws_api:
                    self._ws_api[method](ws, msg.get('data'))
                else:
                    raise rpc.NoSuchFunction
            else:
                raise rpc.InvalidRequest

        except rpc.InvalidRequest as exc:

            ws.logger.warning(str(exc))
            ws.error_message(exc)

        except Exception as exc:

            ws.logger.exception('Unhandlerd excption')
            ws.error_message(exc)

    def _ws_methods(self, app):
        '''Search for web-socket rpc-handlers in all registered extensions.

        A websocket handler is a method prefixed by ``ws_``.
        '''
        for ext in app.extensions:
            for name in dir(ext):
                if name.startswith('ws_'):
                    handler = getattr(app, name, None)
                    if hasattr(handler, '__call__'):
                        name = '_'.join(name.split('_')[1:])
                        yield name, handler
