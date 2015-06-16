import json
from unittest import skipUnless

from pulsar.apps.test import test_timeout, check_server

from lux.utils import test


REDIS_OK = check_server('redis')


@skipUnless(REDIS_OK, 'Requires a running Redis server')
@test_timeout(20)
class TestSqlite(test.AppTestCase):
    config_file = 'tests.sessions'
    config_params = {'DATASTORE': 'sqlite://'}

    @classmethod
    def setUpClass(cls):
        cls.config_params['CACHE_SERVER'] = ('redis://%s' %
                                             cls.cfg.redis_server)
        return super().setUpClass()

    def test_backend(self):
        backend = self.app.auth_backend
        self.assertTrue(backend)
        self.assertEqual(len(backend.backends), 2)

    @test.green
    def test_get_user_none(self):
        backend = self.app.auth_backend
        request = self.app.wsgi_request()
        user = backend.get_user(request, user_id=18098098)
        self.assertEqual(user, None)
        user = backend.get_user(request, email='ksdcks.sdvddvf@djdjhdfc.com')
        self.assertEqual(user, None)
        user = backend.get_user(request, username='dhvfvhsdfgvhfd')
        self.assertEqual(user, None)

    @test.green
    def test_create_user(self):
        backend = self.app.auth_backend
        request = self.app.wsgi_request()

        user = backend.create_user(request,
                                   username='pippo',
                                   email='pippo@pippo.com',
                                   password='pluto',
                                   first_name='Pippo')
        self.assertTrue(user.id)
        self.assertEqual(user.first_name, 'Pippo')
        self.assertFalse(user.is_superuser())
        self.assertFalse(user.is_active())

        # make it active
        with self.app.odm().begin() as session:
            user.active = True
            session.add(user)

        self.assertTrue(user.is_active())

    @test.green
    def test_create_superuser(self):
        backend = self.app.auth_backend
        request = self.app.wsgi_request()

        user = backend.create_superuser(request,
                                        username='foo',
                                        email='foo@pippo.com',
                                        password='pluto',
                                        first_name='Foo')
        self.assertTrue(user.id)
        self.assertEqual(user.first_name, 'Foo')
        self.assertTrue(user.is_superuser())
        self.assertTrue(user.is_active())

    def test_get(self):
        request = yield from self.client.get('/')
        response = request.response
        self.assertEqual(response.status_code, 200)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())

    def test_login_fail(self):
        data = {'username': 'jdshvsjhvcsd',
                'password': 'dksjhvckjsahdvsf'}
        request = yield from self.client.post('/api/authorizations',
                                              content_type='application/json',
                                              body=data)
        response = request.response
        self.assertEqual(response.status_code, 403)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())
        self.json(response)
        #
        request = yield from self.client.get('/login')
        response = request.response
        self.assertEqual(response.status_code, 200)
        token = self.authenticity_token(self.bs(response))
        self.assertTrue(token)
        data.update(token)
        cookie = self.cookie(response)
        self.assertTrue(cookie)
        request = yield from self.client.post('/api/authorizations',
                                              content_type='application/json',
                                              body=data,
                                              cookie=cookie)
        response = request.response
        self.assertEqual(response.status_code, 200)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())
        self.json(response)

    def test_create_superuser_command_and_login(self):
        username = test.randomname()
        email = '%s@jgjh.com' % username
        password = 'dfbjdhbvdjbhv'
        data = {'username': username,
                'password': password}
        user = yield from self.create_superuser(username, email, password)
        self.assertEqual(user.username, username)
        self.assertNotEqual(user.password, password)

        request = yield from self.client.get('/login')
        response = request.response
        self.assertEqual(response.status_code, 200)
        token = self.authenticity_token(self.bs(response))
        self.assertTrue(token)
        data.update(token)
        cookie = self.cookie(response)
        self.assertTrue(cookie)
        #
        # Login with csrf token and cookie, It should work
        request = yield from self.client.post('/api/authorizations',
                                              content_type='application/json',
                                              body=data,
                                              cookie=cookie)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue(data)
        cookie2 = self.cookie(response)
        # The cookie has changed
        self.assertNotEqual(cookie, cookie2)
        #
        request = yield from self.client.get('/', cookie=cookie2)
        response = request.response
        self.assertEqual(response.status_code, 200)
        user = request.cache.user
        self.assertTrue(user.is_authenticated())
        cookie3 = self.cookie(response)
        # The cookie has changed
        self.assertEqual(cookie3, None)
        #
        request = yield from self.client.get('/login', cookie=cookie2)
        response = request.response
        self.assertEqual(response.status_code, 302)
        return cookie2

    def test_logout(self):
        cookie = yield from self.test_create_superuser_command_and_login()
        #
        # This wont work, not csrf token
        request = yield from self.client.post('/api/authorizations/logout',
                                              content_type='application/json',
                                              body={},
                                              cookie=cookie)
        response = request.response
        self.assertEqual(response.status_code, 403)
        #
        request = yield from self.client.get('/', cookie=cookie)
        response = request.response
        self.assertEqual(response.status_code, 200)
        user = request.cache.user
        self.assertTrue(user.is_authenticated())
        token = self.authenticity_token(self.bs(response))
        self.assertTrue(token)

        request = yield from self.client.post('/api/authorizations/logout',
                                              content_type='application/json',
                                              body=token,
                                              cookie=cookie)
        response = request.response
        self.assertEqual(response.status_code, 200)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())
        cookie2 = self.cookie(response)
        self.assertTrue(cookie2)
        self.assertNotEqual(cookie, cookie2)
