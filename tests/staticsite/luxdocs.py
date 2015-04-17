import os

from lux.extensions.static import HtmlContent

from . import TestStaticSite, base


class StaticSiteTests(TestStaticSite):
    config_file = 'luxsite'
    config_params = {'STATIC_LOCATION': os.path.join(base, 'docs')}

    def test_build_site(self):
        app = self.app
        site = app.handler.middleware[-1]
        self.assertIsInstance(site, HtmlContent)
        items = site.build(app)
        self.assertTrue(items)
        self.assertTrue(len(items) > 40)
