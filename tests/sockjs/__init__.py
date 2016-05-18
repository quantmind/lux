from lux.core import LuxExtension

from tests.config import *  # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.odm',
              'lux.extensions.auth',
              'lux.extensions.sockjs',
              'tests.odm']

WS_URL = '/testws'
API_URL = ''
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']
DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'
CACHE_SERVER = PUBSUB_STORE = redis_cache_server
PUBSUB_MODELS_BROADCAST = set(['tasks'])


class Extension(LuxExtension):

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
