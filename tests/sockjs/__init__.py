import lux

from tests.config import *  # noqa
from tests.auth import UserRest

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.odm',
              'lux.extensions.auth',
              'lux.extensions.sockjs']

WS_URL = '/testws'
API_URL = ''
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']
DATASTORE = 'sqlite://'


class Extension(lux.Extension):

    def api_sections(self, app):
        return [UserRest()]

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
