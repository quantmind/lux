from lux.utils import test
from lux import forms


class FormLayoutTests(test.TestCase):

    def test_layout_class(self):
        class TestForm(forms.Form):
            name = forms.CharField()
        layout = TestForm.layout
        self.assertTrue(isinstance(layout, forms.Layout))
        self.assertFalse(layout.form_class)
        form = TestForm()
        callable = form.layout
        self.assertTrue(layout.form_class)
        self.assertTrue(hasattr(callable, '__call__'))
        self.assertTrue(len(layout.children), 2)
        form = TestForm()
        self.assertTrue(layout.form_class)

    def test_layout_create(self):
        class TestForm(forms.Form):
            name = forms.CharField()
        form = TestForm()
        html = form.layout()
        self.assertEqual(html.tag, 'form')
        txt = html.render()
        self.assertTrue(txt)
