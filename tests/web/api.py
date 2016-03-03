from tests import web


class ApiTest(web.WebsiteTest):

    async def test_base(self):
        request = await self.client.get('/')
        data = self.json(request.response, 200)
        self.assertTrue(data)
        self.assertTrue('user_url' in data)
