import os

from pulsar.apps.wsgi import WsgiHandler


from . import TestStaticSite, base


class StaticSiteTests(TestStaticSite):
    config_params = {'TEST_DOCS': True,
                     'STATIC_LOCATION': os.path.join(base, 'build2')}

    def test_middleware(self):
        app = self.app
        wsgi = app.handler
        self.assertIsInstance(wsgi, WsgiHandler)
        #
        self.assertEqual(len(wsgi.middleware), 7)

    def test_build_site(self):
        app = self.app
        site = app.handler.middleware[-1]
        items = site.build(app)
        self.assertTrue(items)
        self.assertEqual(len(items), 11)
