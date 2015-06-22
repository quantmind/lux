from pulsar import ImproperlyConfigured

from lux.utils import test


class CommandTests(test.TestCase):
    config_file = 'tests.core'

    def test_require(self):
        app = self.application()
        self.assertRaises(ImproperlyConfigured,
                          app.require, 'djbdvb.vkdjfbvkdf')

    def test_cms_attributes(self):
        app = self.application()
        cms = app.cms
        self.assertEqual(cms.app, app)
        self.assertEqual(cms.key, None)
        self.assertEqual(cms._sitemap, None)

    def test_cms_page(self):
        app = self.application()
        page = app.cms.page('')
        self.assertTrue(page)
        self.assertEqual(page['path'], '/')
        self.assertEqual(page['template'], 'home.html')
        self.assertIsInstance(app.cms._sitemap, list)

    def test_cms_page(self):
        app = self.application()
        page = app.cms.page('')
        self.assertTrue(page)
        self.assertEqual(page.path, '/')
        self.assertEqual(page.template, 'home.html')
        self.assertIsInstance(app.cms._sitemap, list)

    def test_cms_no_page(self):
        app = self.application()
        page = app.cms.page('xxx')
        self.assertFalse(page)
        self.assertEqual(page.path, None)
        self.assertEqual(page.template, None)
        self.assertIsInstance(app.cms._sitemap, list)
