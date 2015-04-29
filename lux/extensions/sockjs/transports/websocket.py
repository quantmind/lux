import logging

from pulsar import Http404
from pulsar.apps import ws

from . import Transport


class WebSocketProtocol(ws.WebSocketProtocol, Transport):
    name = 'websocket'
    _logger = logging.getLogger('lux.sockjs')

    def on_open(self, client):
        self.logger.info('Opened a new websocket connection %s', client)
        self._hartbeat(client, 'o')

    def _hartbeat(self, client, b):
        connection = self.connection
        if not connection or connection.closed:
            return
        if b == 'h':
            self.logger.debug('Hartbeat message  %s', client)

        self.write(b)
        self._loop.call_later(self.config['WEBSOCKET_HARTBEAT'],
                              self._hartbeat, client, 'h')


class WebSocket(ws.WebSocket):
    '''WebSocket wsgi handler with new protocol class
    '''
    protocol_class = WebSocketProtocol

    def get(self, request):
        if not request.config['WEBSOCKET_AVAILABLE']:
            raise Http404
        return super().get(request)
