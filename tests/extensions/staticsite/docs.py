from pulsar.apps.wsgi import WsgiHandler

from lux.utils import test
from lux.extensions.static import HtmlContent

from .static import StaticSiteMixin


class StaticSiteTests(StaticSiteMixin, test.TestCase):
    config_params = {'TEST_DOCS': True,
                     'STATIC_LOCATION': 'tests/extensions/staticsite/build2'}

    def __test_middleware(self):
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
        self.assertEqual(len(items), 10)
