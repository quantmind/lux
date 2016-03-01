from unittest import mock

from lux.utils import test
from lux.extensions.oauth import request_oauths

from tests.config import *  # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.odm',
              'lux.extensions.auth',
              'lux.extensions.oauth']

DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'

AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']

# Just some dummy values for testing
OAUTH_PROVIDERS = {'amazon': {'key': 'fdfvfvfv',
                              'secret': 'fvfvdvdf'},
                   'facebook': {'key': 'fdfvfvfv',
                                'secret': 'fdfvfvfv'},
                   'twitter': {'key': 'fdfvfvfv',
                               'secret': 'fdfvfvfv',
                               'site': '@fdfvfvfv'},
                   'github': {'key': 'fdfvfvfv',
                              'secret': 'fdfvfvfv',
                              'login': True},
                   'google': {'analytics': {'id': 'UA-7718259-1'},
                              'simple_key': 'fdfvfvfv',
                              'key': 'fdfvfvfv',
                              'secret': 'fdfvfvfv',
                              'login': True},
                   'linkedin': {'key': 'fdfvfvfv',
                                'secret': 'fdfvfvfv',
                                'login': True}
                   }


class TestClient(test.TestClient):

    def request_start_response(self, method, path, **kwargs):
        kwargs['https'] = True
        request, start_response = super().request_start_response(
            method, path, **kwargs)
        oauths = request_oauths(request)
        assert oauths
        request.cache.logger = mock.MagicMock()
        http = mock.MagicMock()
        post = mock.MagicMock()
        post.decode_content = mock.MagicMock(
            return_value={'access_token': 'fooo'})
        http.post = mock.MagicMock(return_value=post)
        request.cache.http = http
        return request, start_response


class OAuthTest(test.AppTestCase):
    config_file = 'tests.oauth'

    @classmethod
    def get_client(cls):
        return TestClient(cls.app)
