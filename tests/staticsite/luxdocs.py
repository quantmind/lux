import os
from lux.utils import test
from lux.extensions.static import HtmlContent

from . import StaticSiteMixin


class StaticSiteTests(StaticSiteMixin, test.TestCase):
    config_file = 'luxsite'
    config_params = {'STATIC_LOCATION': os.path.join(os.path.dirname(__file__),
                                                     'docs')}

    def test_build_site(self):
        app = self.application()
        site = app.handler.middleware[-1]
        self.assertIsInstance(site, HtmlContent)
        items = site.build(app)
        self.assertTrue(items)
        self.assertTrue(len(items) > 40)
