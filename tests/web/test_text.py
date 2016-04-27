from urllib.parse import urlsplit

from tests import web


class ContentTest(web.WebsiteTest):

    async def test_get(self):
        request = await self.webclient.get('/articles/test')
        bs = self.bs(request.response, 200)
        self.assertEqual(str(bs.title), '<title>Just a test</title>')

    async def test_get_settings_404(self):
        request = await self.webclient.get('/settings')
        self.assertEqual(request.response.status_code, 404)

    async def test_get_settings_foo_404(self):
        request = await self.webclient.get('/settings/foo')
        self.assertEqual(request.response.status_code, 404)

    async def test_get_settings_foo_303(self):
        request = await self.webclient.get('/testing')
        self.assertEqual(request.response.status_code, 302)
        location = request.response['location']
        self.assertTrue(urlsplit(location).path, '/testing/bla')

    async def test_get_sitemap(self):
        request = await self.webclient.get('/sitemap.xml')
        bs = self.xml(request.response, 200)
        sitemap = bs.findAll('sitemap')
        self.assertTrue(sitemap)
