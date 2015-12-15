from lux.utils import test
from lux.extensions.admin import Admin


class AdminTest(test.AppTestCase):
    config_file = 'tests.admin'

    def test_app(self):
        request = self.app.wsgi_request(path='/admin')
        admin = self.app.extensions['lux.extensions.admin'].admin
        self.assertIsInstance(admin, Admin)
        sitemap = admin.sitemap(request)
        self.assertTrue(sitemap)
        self.assertEqual(len(sitemap), 1)
        items = {}
        for site in sitemap:
            items.update(((item['title'], item) for item in site['items']))
        self.assertEqual(len(items), 1)
        blog = items['Blogs']
        self.assertEqual(blog['icon'], 'fa fa-book')
        self.assertEqual(blog['title'], 'Blogs')
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
