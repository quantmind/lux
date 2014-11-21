from pulsar.apps.wsgi import WsgiHandler

from lux.utils import test
from lux.extensions.static import HtmlContent

from . import StaticSiteMixin


class StaticSiteTests(StaticSiteMixin, test.TestCase):

    def test_middleware(self):
        app = self.application()
        wsgi = app.handler
        self.assertIsInstance(wsgi, WsgiHandler)
        #
        self.assertEqual(len(wsgi.middleware), 6)

    def test_build_site(self):
        app = self.application()
        site = app.handler.middleware[-1]
        self.assertIsInstance(site, HtmlContent)
        items = site.build(app)
        self.assertTrue(items)
        self.assertEqual(len(items), 7)
        #
        # last file should be the index.html
        item = items[-1]
        self.assertTrue(item.file.endswith('/index.html'))

    def test_blog_post(self):
        app = self.application()
        site = app.handler.middleware[-1]
        items = site.build(app)
        for item in items:
            if item and item.file.endswith('/blog1.html'):
                return
        raise Exception('Could not fine blog1.html')
