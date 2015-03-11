import os

import bs4

from pulsar.apps.test import test_timeout
from pulsar.apps.http import HttpClient

import lux
from lux.utils import test
from lux.extensions.odm import database_drop


class TestAuthSite(test.TestServer):
    config_file = 'tests.website'

    @classmethod
    @test_timeout(30)
    def setUpClass(cls):
        yield from super().setUpClass()
        yield from cls.app.get_command('create_superuser')(
            ['--username', 'pippo', '--password', 'pluto'])

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

    @test_timeout(10)
    def test_login(self):
        http = HttpClient()
        url = self.url + self.app.config['LOGIN_URL']
        response = yield from http.get(url)
        cookie = response.cookies.get('luxtest')
        self.assertTrue(cookie)
        self.assertEqual(response.status_code, 200)
        doc = self.bs(response)
        token = self.authenticity_token(doc)
        self.assertEqual(len(token), 1)
        # try to login
        data = {'username': 'pippo', 'password': 'pluto'}
        response2 = yield from http.post(url, data=data)
        self.assertEqual(response2.status_code, 403)
        #
        # Add csrf token
        data.update(token)
        response2 = yield from http.post(url, data=data)
        self.assertEqual(response2.status_code, 200)
        cookie2 = response2.cookies.get('luxtest')
        self.assertTrue(cookie2)
        self.assertNotEqual(cookie2.value, cookie.value)
        self.assertEqual(response2.headers['content-type'],
                         'application/json; charset=utf-8')
        data = response2.json()
        self.assertTrue('redirect' in data)
        self.assertEqual(data['success'], True)
        #
        # Login again should cause MethodNotAllowed
        response3 = yield from http.post(url, data=data)
        self.assertEqual(response3.status_code, 405)

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
