from pulsar.api import ImproperlyConfigured

from lux.utils import test


class CommandTests(test.TestCase):
    config_file = 'tests.core'

    def test_clone(self):
        groups = {'site': {'path': '*'}}
        app = self.application()
        callable = app.clone_callable(CONTENT_GROUPS=groups)
        self.assertNotEqual(app.callable, callable)
        app2 = callable.setup()
        self.assertEqual(app2.config['CONTENT_GROUPS'], groups)

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
        page = app.cms.page('')
        self.assertTrue(page)
        self.assertEqual(page.path, '')
        self.assertEqual(page.body_template, 'home.html')
        sitemap = app.cms.sitemap()
        self.assertIsInstance(sitemap, list)
        self.assertEqual(id(sitemap), id(app.cms.sitemap()))

    def test_cms_wildcard(self):
        app = self.application()
        page = app.cms.page('xxx')
        self.assertTrue(page)
        self.assertEqual(page.path, '')
        self.assertEqual(page.urlargs, {'path': 'xxx'})
        self.assertEqual(page.body_template, 'home.html')
        self.assertIsInstance(app.cms.sitemap(), list)

    def test_cms_path_page(self):
        app = self.application()
        page = app.cms.page('bla/foo')
        self.assertTrue(page)
        self.assertEqual(page.path, 'bla')
        self.assertEqual(page.body_template, 'bla.html')
        self.assertIsInstance(app.cms.sitemap(), list)

    def test_extension_override(self):
        app = self.application()
        self.assertTrue('RANDOM_P' in app.config)
        self.assertTrue('USE_ETAGS' in app.config)
        self.assertTrue('SERVE_STATIC_FILES' in app.config)
