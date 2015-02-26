from pulsar.apps.test import test_timeout

import lux
from lux.utils import test
from lux.extensions.odm import database_drop


class TestAuthSite(test.TestServer):
    config_file = 'tests.auth_ext'

    def __test_home(self):
        response = yield from self.http.get(self.url)
        self.assertEqual(response.status_code, 200)
