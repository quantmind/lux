import lux

from tests.config import *  # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.sockjs']

WS_URL = '/testws'


class Extension(lux.Extension):

    def ws_add(self, request):
        """Add two numbers
        """
        a = request.params.get('a', 0)
        b = request.params.get('b', 0)
        request.send_result(a+b)

    def ws_echo(self, request):
        """Echo parameters
        """
        request.send_result(request.params)
