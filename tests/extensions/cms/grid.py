import lux
from lux.extensions.cms import templates
from lux.extensions.cms.grid import PageTemplate, Row, Column, Grid, Context

from tests.extensions import cms as test


class TestTemplates(test.TestCase):

    def page(self):
        page = PageTemplate(
            Grid(role='header'),
            Grid(Row(Column(Context('sidebar', tag='div'), span=0.25),
                     Column(Context('content', tag='div'), span=0.75)),
                 role='main'),
            Grid(role='footer'))
        return page

    def testPage(self):
        page = self.page()
        self.assertEqual(page.parameters.role, 'page')
        self.assertEqual(len(page.children), 3)
        self.assertEqual(page.children[0].parameters.role, 'header')
        self.assertEqual(page.children[1].parameters.role, 'main')
        self.assertEqual(page.children[2].parameters.role, 'footer')

    def testRenderPage(self):
        page = self.page()
        html = yield page(context={'content': 'Ciao'})
        self.assertTrue(isinstance(html, lux.Html))
        text = html.render()
        self.assertTrue('Ciao' in text)

    def test_nav_template(self):
        page = templates.nav_page
        self.assertEqual(page.parameters.role, 'page')
        self.assertEqual(len(page.children), 3)
        for child in page.children:
            self.assertIsInstance(child, Grid)
        request = self.request()
        html = request.html_document
        html = yield page(request)
        self.assertEqual(html.tag, 'div')
