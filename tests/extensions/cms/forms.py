from lux.utils import test
from lux.extensions.cms import ContentForm


class FormLayoutTests(test.TestCase):

    def test_contentform_layout(self):
        layout = ContentForm.layout
        form = ContentForm(initial={'content_type': 'testing'})
        callable = form.layout
        self.assertTrue(layout.form_class)
        self.assertTrue(hasattr(callable, '__call__'))
        self.assertEqual(len(layout.children), 4)
        html = callable()
        self.assertEqual(html.tag, 'form')
        text = html.render()
        self.assertTrue(text.startswith('<form'))
