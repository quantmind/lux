import os
from bs4 import BeautifulSoup as bs

from lux.extensions.gae.test import TestCase
from lux.extensions.gae import Registration


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
        request = self.request(path='/pluto')
        response = request.response
        # we get a redirect to login
        self.assertEqual(response.status_code, 404)

    def test_user_ok(self):
        request = self.request()
        auth = request.cache.auth_backend
        user = auth.create_user(request, username='test45')
        self.assertEqual(user.username, 'test45')
        request = self.request(path='/test45', HTTP_ACCEPT='text/html')
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

    def test_registration(self):
        app = self.application()
        request = self.request(app, path='/signup')
        response = request.response
        self.assertEqual(response.status_code, 200)
        cookie = 'luxgaeblog=%s' % request.cache.session.key.id()
        headers = [('cookie', cookie)]
        doc = bs(response.content[0])
        data = self.authenticity_token(doc)

        data.update({'username': 'user67',
                     'email': 'user67@fff.com',
                     'password': 'password',
                     'password_repeat': 'password'})
        request = self.post(app, path='/signup', body=data, headers=headers)
        response = request.response
        self.assertEqual(response.status_code, 200)

        #self.assertEqual(user.username, 'user4')
        #message = app._outbox.pop()
        #self.assertEqual(message[1], 'user4@bla.com')
        #body = message[3]

    def test_password_reset(self):
        app = self.application()
        request = self.request(app, path='/reset-password')
        response = request.response
        self.assertEqual(response.status_code, 200)
        cookie = 'luxgaeblog=%s' % request.cache.session.key.id()
        headers = [('cookie', cookie)]
        doc = bs(response.content[0])
        data = self.authenticity_token(doc)
        # create user
        auth = request.cache.auth_backend
        user = auth.create_user(request, username='user4',
                                email='user4@bla.com',
                                password='abcdfg', active=True)
        self.assertEqual(user.username, 'user4')
        data['email'] = 'user4@bla.com'

        request = self.post(app, path='/reset-password',
                            headers=headers, body=data)
        response = request.response
        self.assertEqual(response.status_code, 200)
        #
        message = app._outbox.pop()
        self.assertEqual(message[1], 'user4@bla.com')
        body = message[3]
        rs = Registration.query(Registration.user == user.key).fetch(10)
        self.assertEqual(len(rs), 1)
        rs = rs[0]
        self.assertTrue(rs.key.id() in body)
        #
        # Now follow the link
        url = path='/reset-password/%s' % rs.key.id()
        request = self.request(app, path=url)
        response = request.response
        self.assertEqual(response.status_code, 200)
        doc = bs(response.content[0])
        data = self.authenticity_token(doc)
        #self.assertTrue(doc.find('input', attrs={'name': 'password'}))
        #self.assertTrue(doc.find('input', attrs={'name': 'password_repeat'}))
        #
        # Now post the change password
        url = url + '/reset'
        cookie = 'luxgaeblog=%s' % request.cache.session.key.id()
        headers = [('cookie', cookie)]
        data['password'] = 'newpassword'
        data['password_repeat'] = 'newpassword'
        request = self.post(app, path=url, headers=headers, body=data)
        response = request.response
        self.assertEqual(response.status_code, 200)

    def test_css(self):
        command = self.fetch_command('style')
        result = command(['--cssfile', 'teststyle'], dump=False)
        self.assertFalse(os.path.isfile(result))
        self.assertTrue(result)
