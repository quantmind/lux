import os

from pulsar.apps.test import test_timeout
from pulsar.apps.http import HttpClient

import lux
from lux.utils import test
from lux.extensions.odm import database_drop


class TestAuthSite(test.TestServer):
    config_file = 'tests.website'

    @classmethod
    def setUpClass(cls):
        yield from super().setUpClass()
        yield from cls.app.get_command('create_superuser')(
            [], interactive=False, username='pippo', password='pluto')

    def test_css(self):
        command = self.app.get_command('style')
        result = yield from command(['--cssfile', 'teststyle'], dump=False)
        self.assertFalse(os.path.isfile(result))
        self.assertTrue(result)

    def test_home(self):
        http = HttpClient()
        response = yield from http.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'],
                         'text/html; charset=utf-8')
        cookie = response.cookies.get('luxtest')
        self.assertTrue(cookie)
        self.assertTrue(cookie.value)
        response = yield from http.get(self.url)
        cookie2 = response.cookies.get('luxtest')
        self.assertFalse(cookie2)

    def test_login(self):
        http = HttpClient()
        url = self.url + self.app.config['LOGIN_URL']
        response = yield from http.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reset_password(self):
        http = HttpClient()
        url = self.url + self.app.config['RESET_PASSWORD_URL']
        response = yield from http.get(url)
        self.assertEqual(response.status_code, 200)

    def test_404(self):
        http = HttpClient()
        url = self.url + '/dkvshcvsdkchsdkc'
        response = yield from http.get(url)
        self.assertEqual(response.status_code, 404)
