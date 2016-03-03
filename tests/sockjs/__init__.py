import lux

from tests.config import *  # noqa
from tests.auth import UserRest

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.odm',
              'lux.extensions.auth',
              'lux.extensions.sockjs',
              'tests.odm']

WS_URL = '/testws'
API_URL = ''
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']
DATASTORE = 'sqlite://'
CACHE_SERVER = PUBSUB_STORE = redis_cache_server
BROADCAST_CHANNELS = set(['tasks'])


class Extension(lux.Extension):

    def api_sections(self, app):
        return [UserRest()]

    def ws_add(self, request):
        """Add two numbers
        """
        a = request.params.get('a', 0)
        b = request.params.get('b', 0)
        return a + b

    def ws_echo(self, request):
        """Echo parameters
        """
        return request.params
