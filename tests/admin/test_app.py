from unittest import mock

from lux.utils import test
from lux.extensions.admin import Admin


class AdminTest(test.AppTestCase):
    config_file = 'tests.admin'

    @classmethod
    def create_test_application(cls):
        """Return the lux application"""
        app = super().create_test_application()
        app.api = mock.MagicMock()
        return app

    def test_app(self):
        request = self.app.wsgi_request(path='/admin')
        admin = self.app.extensions['lux.extensions.admin'].admin
        self.assertIsInstance(admin, Admin)
        sitemap = admin.sitemap(request)
        self.assertTrue(sitemap)
        self.assertEqual(len(sitemap), 2)
        items = {}
        for site in sitemap:
            items.update(((item['title'], item) for item in site['items']))
        self.assertEqual(len(items), 6)
        blog = items['Blog']
        self.assertEqual(blog['icon'], 'fa fa-book')
        self.assertEqual(blog['title'], 'Blog')
        self.assertEqual(blog['href'], '/admin/blog')

    async def test_admin_home_view(self):
        request = await self.client.get('/admin')
        response = request.response
        self.assertEqual(response.status_code, 200)

    async def test_list_view(self):
        request = await self.client.get('/admin/blog')
        response = request.response
        self.assertEqual(response.status_code, 200)

    async def test_add_view(self):
        request = await self.client.get('/admin/blog/add')
        response = request.response
        self.assertEqual(response.status_code, 200)

    async def test_edit_view(self):
        request = await self.client.get('/admin/blog/1')
        response = request.response
        self.assertEqual(response.status_code, 200)
