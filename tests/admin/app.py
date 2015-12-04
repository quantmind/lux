from lux.utils import test
from lux.extensions.admin import Admin


class AdminTest(test.AppTestCase):
    config_file = 'tests.admin'

    def test_app(self):
        app = self.app
        admin = self.app.extensions['lux.extensions.admin'].admin
        self.assertIsInstance(admin, Admin)
        sitemap = admin.sitemap(app)
        self.assertTrue(sitemap)
        self.assertEqual(len(sitemap), 1)
        items = {}
        for site in sitemap:
            items.update(((item['title'], item) for item in site['items']))
        self.assertEqual(len(items), 1)
        blog = items['Blog']
        self.assertEqual(blog['icon'], 'fa fa-book')
        self.assertEqual(blog['title'], 'Blog')
        self.assertEqual(blog['href'], '/admin/blogs')

    def test_admin_home_view(self):
        request = yield from self.client.get('/admin')
        response = request.response
        self.assertEqual(response.status_code, 200)

    def test_list_view(self):
        request = yield from self.client.get('/admin/blogs')
        response = request.response
        self.assertEqual(response.status_code, 200)

    def test_add_view(self):
        request = yield from self.client.get('/admin/blogs/add')
        response = request.response
        self.assertEqual(response.status_code, 200)

    def test_edit_view(self):
        request = yield from self.client.get('/admin/blogs/1')
        response = request.response
        self.assertEqual(response.status_code, 200)
