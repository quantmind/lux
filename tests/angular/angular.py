from pulsar.apps.test import mock

from lux.utils import test

from lux.extensions.angular import Router


def example(url=''):
    return Router(url,
                  Router('bla'),
                  Router('foo/'),
                  html_body_template='foo.html')


class AngularTest(test.TestCase):
    config_file = 'angular'

    def test_properties(self):
        router = example()
        self.assertEqual(router.uirouter, 'lux.ui.router')
        self.assertFalse(router.route.is_leaf)
        self.assertEqual(router.html_body_template, 'foo.html')
        self.assertEqual(len(router.routes), 2)

    def test_sitemap(self):
        app = self.application()
        app.html_response = mock.MagicMock()
        router = example()
        request = app.wsgi_request()
        response = router.get(request)
        jscontext = request.html_document.jscontext
        self.assertTrue('pages' in jscontext)
        pages = jscontext['pages']
        self.assertEqual(len(pages), 4)
