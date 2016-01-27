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
        bs = self.bs(request.response, 200)