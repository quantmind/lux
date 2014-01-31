from pulsar.apps.ws import WebSocket, WS

import lux
from lux import Router, Html


bitcoin_data = '/bitcoin-data'


class Extension(lux.Extension):
    '''bitcoin extension
    '''
    def middleware(self, app):
        return [Router('/bitcoin', get=self.home),
                WebSocket(bitcoin_data, BitCoin())]

    def home(self, request):
        doc = request.html_document
        scheme = 'wss' if request.is_secure else 'ws'
        url = request.absolute_uri(bitcoin_data, scheme=scheme)
        doc.body.data('bitcoinurl', url)
        doc.head.scripts.require('bitcoin/bitcoin.js')
        html = Html('div', '<p>bitcoin is created!</p>')
        return html.http_response(request)


class BitCoin(WS):
    pass
