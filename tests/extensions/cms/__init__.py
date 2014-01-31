import lux
from lux.utils import test


class TestCase(test.TestCase):
    config_params = {'EXTENSIONS': test.all_extensions()}

    def application(self):
        # Minimalist application for testing this extensions
        app = lux.App(__file__)
        self.assertTrue('ui' in app.extensions)
        self.assertTrue('base' in app.extensions)
        self.assertTrue('sitemap' in app.extensions)
        return app
