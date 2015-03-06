from lux.utils import test


class AngularTest(test.TestCase):
    config_file = 'tests.angular_ext'

    def test_properties(self):
        app = self.application()
        request = self.request(app)
        router = request.app_handler
        self.assertEqual(router.uirouter, 'lux.ui.router')
        self.assertFalse(router.route.is_leaf)
        self.assertEqual(router.html_body_template, 'foo.html')
        self.assertEqual(len(router.routes), 2)

    def test_sitemap(self):
        app = self.application()
        request = self.request(app)
        router = request.app_handler
        response = request.response
        jscontext = request.html_document.jscontext
        self.assertTrue('pages' in jscontext)
        pages = jscontext['pages']
        self.assertEqual(len(pages), 4)
