import lux
from lux import Template
from lux.utils import test


class TestHtml(test.TestCase):
    config_file = 'luxpy.config'

    def test_doc(self):
        app = self.application()
        request = app.wsgi_request()
        doc = request.html_document
        self.assertEqual(doc, request.html_document)
        request2 = app.wsgi_request()
        self.assertNotEqual(doc, request2.html_document)

    def test_template(self):
        template = Template(key='foo')
        self.assertEqual(template.key, 'foo')
        html = template(context={'foo': 'Hello'})
        self.assertEqual(html.render(), 'Hello')
        #
        template = Template(tag='div', key='foo')
        self.assertEqual(template.tag, 'div')
        self.assertEqual(template.key, 'foo')
        html = template(context={'foo': 'Hello'})
        self.assertEqual(html.render(), '<div>Hello</div>')
