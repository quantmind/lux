from lux.utils import test
from lux import forms
from lux.forms import Layout, Fieldset, Submit


class TestAForm1(forms.Form):
    name = forms.CharField()


Layout1 = Layout(TestAForm1)

Layout2 = Layout(TestAForm1,
                 Fieldset(all=True),
                 Submit('done'))


class PageForm(forms.Form):
    url = forms.UrlField(lux_directive='foo')
    markup = forms.ChoiceField(options=('bla', 'foo'))
    body = forms.CharField(type='textarea', required=False)


PageForm1 = Layout(PageForm)


class FormAngularLayoutTests(test.TestCase):

    def _field(self, data, idx):
        self.assertEqual(len(data['children']), 1)
        data = data['children'][0]
        self.assertEqual(data['type'], 'fieldset')
        return data['children'][idx]

    def test_layout_class(self):
        self.assertTrue(Layout1.form_class)
        self.assertEqual(Layout1.form_class, TestAForm1)
        self.assertEqual(len(Layout1.children), 1)

    def test_form_data(self):
        form = Layout1()
        data = form.as_dict()
        self.assertEqual(len(data), 2)
        self.assertEqual(data['type'], 'form')
        self.assertEqual(len(data['children']), 1)

    def test_render_form(self):
        form = Layout1()
        html = form.as_form()
        self.assertEqual(html.tag, 'lux-form')
        self.assertEqual(len(html.children), 0)

    def test_render_form_width_button(self):
        form = Layout2()
        data = form.as_dict()
        self.assertEqual(len(data['children']), 2)

    def test_textarea(self):
        form = PageForm1()
        data = form.as_dict()
        self.assertEqual(len(data['children']), 1)
        data = data['children'][0]
        self.assertEqual(data['type'], 'fieldset')
        self.assertEqual(len(data['children']), 3)
        textarea = data['children'][2]
        self.assertEqual(textarea['type'], 'textarea')
        choice = data['children'][1]
        self.assertEqual(choice['type'], 'select')

    def test_select_field(self):
        form = PageForm1()
        data = form.as_dict()
        self.assertEqual(len(data['children']), 1)
        data = data['children'][0]
        self.assertEqual(data['type'], 'fieldset')
        self.assertEqual(len(data['children']), 3)
        markup = data['children'][1]
        self.assertEqual(markup['type'], 'select')
        options = markup['options']
        self.assertEqual(len(options), 2)
        self.assertTrue(markup['required'])

    def test_validation_attribute(self):
        form = PageForm1()
        data = form.as_dict()
        url = self._field(data, 0)
        self.assertEqual(url['validation_error'], 'Not a valid url')
        self.assertEqual(url['lux-directive'], 'foo')
