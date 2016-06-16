from tests import web


class ApiTest(web.WebsiteTest):

    async def test_base(self):
        request = await self.client.get('/')
        data = self.json(request.response, 200)
        self.assertTrue(data)
        self.assertTrue('user_url' in data)

    # CONTENT API
    async def test_article_list(self):
        request = await self.client.get('/contents/articles?priority:gt=0')
        data = self.json(request.response, 200)['result']
        self.assertEqual(len(data), 3)

    async def test_article_list_priority_query(self):
        request = await self.client.get(
            '/contents/articles?priority=3&priority=2')
        data = self.json(request.response, 200)['result']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['priority'], 2)
        self.assertEqual(data[0]['title'], 'Just a test')

    async def test_options_article_links(self):
        request = await self.client.options('/contents/articles/_links')
        self.assertEqual(request.response.status_code, 200)

    async def test_article_links(self):
        request = await self.client.get('/contents/articles/_links')
        data = self.json(request.response, 200)['result']
        self.assertEqual(len(data), 2)

    async def test_options_article(self):
        request = await self.client.options('/contents/articles/fooo')
        self.assertEqual(request.response.status_code, 200)

    async def test_get_article_404(self):
        request = await self.client.get('/contents/articles/fooo')
        self.json(request.response, 404)

    async def test_head_article_404(self):
        request = await self.client.head('/contents/articles/fooo')
        self.assertEqual(request.response.status_code, 404)

    async def test_get_article_200(self):
        request = await self.client.get('/contents/articles/test')
        data = self.json(request.response, 200)
        self.assertEqual(data['path'], '/articles/test')

    async def test_head_article_200(self):
        request = await self.client.head('/contents/articles/test')
        self.assertEqual(request.response.status_code, 200)
