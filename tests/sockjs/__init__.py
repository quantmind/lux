import lux
from lux.extensions.sockjs import RpcWsMethod

from tests.config import *  # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.sockjs']

WS_URL = '/testws'


class AddWsRpc(RpcWsMethod):

    def on_response(self, data):
        a = data.get('a', 1)
        b = data.get('b', 2)
        self.write(a+b)


class Extension(lux.Extension):

    ws_add = AddWsRpc

    def ws_echo(self, ws, msg):
        ws.write(msg)
