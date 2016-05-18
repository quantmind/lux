from pulsar import ImproperlyConfigured

from lux.utils import test


class CommandTests(test.TestCase):
    config_file = 'tests.core'

    def test_clone(self):
        template = {'/': 'foo.html'}
        app = self.application()
        callable = app.clone_callable(HTML_TEMPLATES=template)
        self.assertNotEqual(app.callable, callable)
        app2 = callable.setup()
        self.assertEqual(app2.config['HTML_TEMPLATES'], template)

    def test_require(self):
        app = self.application()
        self.assertRaises(ImproperlyConfigured,
                          app.require, 'djbdvb.vkdjfbvkdf')

    def test_cms_attributes(self):
        app = self.application()
        cms = app.cms
        self.assertEqual(cms.app, app)

    def test_cms_page(self):
        app = self.application()
        request = app.wsgi_request()
        page = app.cms.page(request, '')
        self.assertTrue(page)
        self.assertEqual(page.path, '/')
        self.assertEqual(page.template, 'home.html')
        sitemap = app.cms.sitemap(request)
        self.assertIsInstance(sitemap, list)
        self.assertEqual(id(sitemap), id(app.cms.sitemap(request)))

    def test_cms_no_page(self):
        app = self.application()
        request = app.wsgi_request()
        page = app.cms.page(request, 'xxx')
        self.assertFalse(page)
        self.assertEqual(page.path, None)
        self.assertEqual(page.template, None)
        self.assertIsInstance(app.cms.sitemap(request), list)

    def test_cms_path_page(self):
        app = self.application()
        request = app.wsgi_request()
        page = app.cms.page(request, 'bla/foo')
        self.assertTrue(page)
        self.assertEqual(page.path, '/bla/<path:path>')
        self.assertEqual(page.template, 'bla.html')
        self.assertIsInstance(app.cms.sitemap(request), list)
