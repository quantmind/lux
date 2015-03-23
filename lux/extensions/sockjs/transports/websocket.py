import logging

from pulsar import Http404
from pulsar.apps import ws

from . import Transport


class WebSocketProtocol(ws.WebSocketProtocol, Transport):
    name = 'websocket'
    _logger = logging.getLogger('lux.sockjs')

    def on_open(self, client, *args):
        if not args:
            self.logger.info('Opened a new websocket connection %s', client)
            args = ('o',)
        else:
            connection = self.connection
            if not connection or connection.closed:
                return
            self.logger.debug('Hartbeat message  %s', client)
        assert len(args) == 1
        self.write(args[0])
        self._loop.call_later(self.config['WEBSOCKET_HARTBEAT'],
                              self.on_open, client, 'h')


class WebSocket(ws.WebSocket):
    protocol_class = WebSocketProtocol

    def get(self, request):
        if not request.config['WEBSOCKET_AVAILABLE']:
            raise Http404
        return super().get(request)
