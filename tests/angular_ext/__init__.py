import lux
from lux import HtmlRouter
from lux.utils import test


EXTENSIONS = ['lux.extensions.ui',
              'lux.extensions.angular']

ANGULAR_UI_ROUTER = True


class Extension(lux.Extension):

    def middleware(self, app):
        return [HtmlRouter('/',
                       HtmlRouter('bla'),
                       HtmlRouter('foo/'),
                       html_body_template='foo.html')]


class AngularTest(test.TestCase):
    config_file = 'tests.angular_ext'

    def __test_properties(self):
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
