import lux
from lux import Context, Template
from lux.utils import test


class TestHtml(test.TestCase):

    def test_doc(self):
        app = self.application()
        request = app.wsgi_request()
        doc = request.html_document
        self.assertEqual(doc, request.html_document)
        request2 = app.wsgi_request()
        self.assertNotEqual(doc, request2.html_document)

    #    TEMPLATES
    def test_context(self):
        template = Context('foo')
        self.assertEqual(template.key, 'foo')
        html = template(context={'foo': 'Hello'})
        self.assertEqual(html.render(), 'Hello')
        template = Context('foo', tag='div')
        html = template(context={'foo': 'Hello'})
        self.assertEqual(html.render(), "<div>Hello</div>")

    def test_nested_context(self):
        template = Template(Context('foo',
                                    Context('bla', tag='span'),
                                    tag='div'),
                            tag='div', title='ciao')
        html = template(context={'foo': 'pippo', 'bla': 'pluto'})
        txt = html.render()
        self.assertEqual(txt, ("<div title='ciao'>"
                               "<div><span>pluto</span>pippo</div>"
                               "</div>"))

    #    SCRIPTS
    def test_required(self):
        app = self.application()
        request = app.wsgi_request()
        doc = request.html_document
        scripts = doc.head.scripts
        self.assertEqual(len(scripts.required), 0)

    def test_required_unknown_local(self):
        app = self.application()
        request = app.wsgi_request()
        doc = request.html_document
        scripts = doc.head.scripts
        self.assertEqual(len(scripts.required), 0)
        scripts.require('jstest/blafoo.js')
        self.assertEqual(len(scripts.required), 1)
        self.assertEqual(scripts.required[-1], '/static/jstest/blafoo.min.js')

    def test_required_unknown_local_not_minified(self):
        app = self.application(MINIFIED_MEDIA=False)
        request = app.wsgi_request()
        doc = request.html_document
        scripts = doc.head.scripts
        scripts.require('jstest/blafoo.js')
        self.assertEqual(len(scripts.required), 1)
        self.assertEqual(scripts.required[-1], '/static/jstest/blafoo.js')
