from bs4 import BeautifulSoup as bs

from lux.extensions.gae.test import TestCase


class TestAPI(TestCase):
    config_file = 'blogapp.config'

    def test_home(self):
        request = self.request(path='/')
        response = request.response
        self.assertEqual(request.path, '/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertTrue(request.cache.auth_backend)

    def test_drafts_400(self):
        request = self.request(path='/drafts')
        response = request.response
        # we get a redirect to login
        self.assertEqual(response.status_code, 302)

    def test_user_404(self):
        request = self.request(path='/pippo')
        response = request.response
        # we get a redirect to login
        self.assertEqual(response.status_code, 404)

    def test_user_ok(self):
        request = self.request()
        auth = request.cache.auth_backend
        user = auth.create_user(request, username='pippo')
        self.assertEqual(user.username, 'pippo')
        request = self.request(path='/pippo', HTTP_ACCEPT='text/html')
        response = request.response
        # we get a redirect to login
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        app = self.application()
        request = self.request(app, path='/login')
        response = request.response
        self.assertEqual(response.status_code, 200)
        session = request.cache.session
        self.assertTrue(session)
        cookie = response.headers.get('set-cookie')
        val = 'luxgaeblog=%s' % session.key.id()
        self.assertTrue(cookie.startswith(val))
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        doc = bs(response.content[0])
        data = self.authenticity_token(doc)
        #
        request = self.post(app, path='/login')
        response = request.response
        # missing CSRF
        self.assertEqual(response.status_code, 403)
        # missing cookie
        request = self.post(app, path='/login', body=data)
        response = request.response
        self.assertEqual(response.status_code, 403)
        #
        headers = [('cookie', val)]
        request = self.post(app, path='/login', body=data, headers=headers)
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertFalse(request.cache.user.is_authenticated())
        #
        auth = request.cache.auth_backend
        user = auth.create_user(request, username='kappa',
                                password='abcdfg', active=True)
        data['username'] = 'kappa'
        data['password'] = 'abcdfg'
        request = self.post(app, path='/login', body=data, headers=headers)
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(request.cache.user.is_authenticated())

