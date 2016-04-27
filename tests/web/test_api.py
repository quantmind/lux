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

    async def test_article_links(self):
        request = await self.client.get('/content/articles/links')
        data = self.json(request.response, 200)['result']
        self.assertEqual(len(data), 2)
        for entry in data:
            url = urlsplit(entry['html_url'])
            self.assertEqual(url.path, entry['path'])
