from lux.core import LuxExtension

from tests.config import *  # noqa

EXTENSIONS = ['lux.ext.base',
              'lux.ext.rest',
              'lux.ext.odm',
              'lux.ext.auth',
              'lux.ext.sockjs',
              'tests.odm']

WS_URL = '/testws'
API_URL = ''
AUTHENTICATION_BACKENDS = ['lux.ext.auth:TokenBackend']
DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'
PUBSUB_STORE = redis_cache_server   # noqa
DEFAULT_POLICY = [
    {
        "resource": "*",
        "action": "*"
    }
]


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
