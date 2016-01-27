from tests import web


class ApiTest(web.WebsiteTest):

    def test_base(self):
        request = yield from self.client.get('/')
        data = self.json(request.response, 200)
        self.assertTrue(data)
        self.assertTrue('user_url' in data)