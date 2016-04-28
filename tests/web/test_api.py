from urllib.parse import urlsplit

from tests import web


class ApiTest(web.WebsiteTest):

    async def test_base(self):
        request = await self.client.get('/')
        data = self.json(request.response, 200)
        self.assertTrue(data)
        self.assertTrue('user_url' in data)

    # CONTENT API
    async def test_article_list(self):
        request = await self.client.get('/content/articles')
        data = self.json(request.response, 200)['result']
        self.assertEqual(len(data), 3)
        for entry in data:
            url = urlsplit(entry['html_url'])
            self.assertEqual(url.path, entry['path'])

    async def test_options_article_links(self):
        request = await self.client.options('/content/articles/_links')
        self.assertEqual(request.response.status_code, 200)

    async def test_article_links(self):
        request = await self.client.get('/content/articles/_links')
        data = self.json(request.response, 200)['result']
        self.assertEqual(len(data), 2)
        for entry in data:
            url = urlsplit(entry['html_url'])
            self.assertEqual(url.path, entry['path'])

    async def test_options_article(self):
        request = await self.client.options('/content/articles/fooo')
        self.assertEqual(request.response.status_code, 200)

    async def test_get_article_404(self):
        request = await self.client.get('/content/articles/fooo')
        self.json(request.response, 404)

    async def test_head_article_404(self):
        request = await self.client.head('/content/articles/fooo')
        self.assertEqual(request.response.status_code, 404)

    async def test_get_article_200(self):
        request = await self.client.get('/content/articles/test')
        data = self.json(request.response, 200)
        self.assertEqual(data['path'], '/articles/test')

    async def test_head_article_200(self):
        request = await self.client.head('/content/articles/test')
        self.assertEqual(request.response.status_code, 200)
