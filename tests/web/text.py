from urllib.parse import urlsplit

from tests import web


class ContentTest(web.WebsiteTest):

    async def test_get(self):
        request = await self.webclient.get('/articles/test')
        bs = self.bs(request.response, 200)
        self.assertEqual(str(bs.title), '<title>Just a test</title>')

    async def test_links(self):
        request = await self.webclient.get('/articles/_links')
        data = self.json(request.response, 200)['result']
        self.assertEqual(len(data), 2)
        for entry in data:
            url = urlsplit(entry['html_url'])
            self.assertEqual(url.path, entry['path'])
