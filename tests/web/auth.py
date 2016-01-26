from tests import web


class AuthTest(web.WebsiteTest):

    def test_web_app(self):
        web = self.web
        self.assertEqual(web.meta.name, 'tests.web.website')

    def test_get_login(self):
        request = yield from self.webclient.get('/login')
        bs = self.bs(request.response, 200)
        self.assertEqual(str(bs.title), '<title>website.com</title>')

    def __test_login_403(self):
        response = yield from self._login(csrf={}, status=403)
        self.assertEqual(response, None)

    def test_login(self):
        token = yield from self._login()
        a = 1
