from pulsar.apps.wsgi import WsgiHandler

from lux.utils import test
from lux.extensions.static import HtmlContent

from . import StaticSiteMixin, base


class StaticSiteTests(StaticSiteMixin, test.TestCase):
    config_params = {'TEST_DOCS': True,
                     'STATIC_LOCATION': base+'build2'}

    def test_middleware(self):
        app = self.application()
        wsgi = app.handler
        self.assertIsInstance(wsgi, WsgiHandler)
        #
        self.assertEqual(len(wsgi.middleware), 7)

    def test_build_site(self):
        app = self.application()
        site = app.handler.middleware[-1]
        self.assertIsInstance(site, HtmlContent)
        items = site.build(app)
        self.assertTrue(items)
        self.assertEqual(len(items), 10)
