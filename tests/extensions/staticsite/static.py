import os
import shutil

from pulsar.apps.wsgi import WsgiHandler

from lux.utils import test
from lux.extensions.static import HtmlContent


class StaticSiteTests(test.TestCase):
    config_file = 'tests.extensions.staticsite.config'

    def tearDown(self):
        if self.apps:
            for app in self.apps:
                dir = os.path.abspath(app.config['STATIC_LOCATION'])
                if os.path.isdir(dir):
                    shutil.rmtree(dir)

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
        self.assertEqual(len(items), 6)
        #
        # last file should be the index.html
        item = items[-1]
        self.assertTrue(item.file.endswith('/index.html'))
