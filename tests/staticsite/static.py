from pulsar.apps.wsgi import WsgiHandler

from . import TestStaticSite


class StaticSiteTests(TestStaticSite):

    def test_middleware(self):
        wsgi = self.app.handler
        self.assertIsInstance(wsgi, WsgiHandler)
        #
        self.assertEqual(len(wsgi.middleware), 6)

    def test_build_site(self):
        app = self.app
        site = app.handler.middleware[-1]
        items = site.build(app)
        self.assertTrue(items)
        self.assertEqual(len(items), 7)

    def test_blog_post(self):
        site = self.app.handler.middleware[-1]
        items = site.build(self.app)
        for item in items:
            if item and item.file.endswith('/blog1.html'):
                return
        raise Exception('Could not file blog1.html')
