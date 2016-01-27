import asyncio

from tests import web


class AuthTest(web.WebsiteTest):

    def test_apps(self):
        self.assertEqual(self.web.meta.name, 'tests.web.website')
        self.assertEqual(self.app.meta.name, 'tests.web.webapi')

    def test_get_login(self):
        request = yield from self.webclient.get('/login')
        bs = self.bs(request.response, 200)
        self.assertEqual(str(bs.title), '<title>website.com</title>')

    def __test_login_403(self):
        response = yield from self._login(csrf={}, status=403)
        self.assertEqual(response, None)

    def test_login(self):
        cookie, token = yield from self._login()
        self.assertTrue(cookie)
        self.assertTrue(token)

    def test_authenticated_view(self):
        cookie, token = yield from self._login()
        request = yield from self.webclient.get('/', cookie=cookie)
        self.bs(request.response, 200)
        self.assertTrue(request.cache.user.is_authenticated())
        self.assertFalse(request.response.cookies)

    def test_invalid_authenticated_view(self):
        cookie, token = yield from self._login()
        request = yield from self.webclient.get('/', cookie=cookie)
        bs = self.bs(request.response, 200)
        self.check_html_token(bs, token)
        self.assertTrue(request.cache.user.is_authenticated())
        self.assertFalse(request.response.cookies)
        # Wait for 5 seconds
        yield from asyncio.sleep(self.app.config['SESSION_EXPIRY']+1)
        # The token is now invalid, the next request with cookie should
        # redirect to the login page
        request = yield from self.webclient.get('/', cookie=cookie)
        response = request.response
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['location'], '/login')
        cookie2 = self.cookie(response)
        self.assertTrue(cookie2)
        self.assertTrue(cookie2.startswith('test-website='))
        self.assertNotEqual(cookie, cookie2)
        self.assertFalse(request.cache.user.is_authenticated())
