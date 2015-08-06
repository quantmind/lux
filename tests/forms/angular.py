from lux.utils import test
from lux import forms
from lux.forms import Layout, Fieldset, Submit


class TestAForm1(forms.Form):
    name = forms.CharField()


Layout1 = Layout(TestAForm1,
                 Fieldset(all=True))

Layout2 = Layout(TestAForm1,
                 Fieldset(all=True),
                 Submit('done'))


class PageForm(forms.Form):
    url = forms.CharField()
    markup = forms.ChoiceField(options=('bla', 'foo'))
    body = forms.CharField(type='textarea', required=False)


PageForm1 = Layout(PageForm,
                   Fieldset(all=True))


class FormAngularLayoutTests(test.TestCase):

    def test_layout_class(self):
        self.assertTrue(Layout1.form_class)
        self.assertEqual(Layout1.form_class, TestAForm1)
        self.assertEqual(len(Layout1.children), 1)

    def test_form_data(self):
        form = Layout1()
        data = form.as_dict()
        self.assertEqual(len(data), 2)
        self.assertEqual(data['field']['type'], 'form')
        self.assertEqual(len(data['children']), 1)

    def test_render_form(self):
        form = Layout1()
        html = form.as_form()
        self.assertEqual(html.tag, 'lux-form')
        self.assertEqual(len(html.children), 1)

    def test_render_form_width_button(self):
        form = Layout2()
        data = form.as_dict()
        self.assertEqual(len(data['children']), 2)

    def test_textarea(self):
        form = PageForm1()
        data = form.as_dict()
        self.assertEqual(len(data['children']), 1)
        data = data['children'][0]
        self.assertEqual(data['field']['type'], 'fieldset')
        self.assertEqual(len(data['children']), 3)
        textarea = data['children'][2]
        self.assertEqual(textarea['field']['type'], 'textarea')
        choice = data['children'][1]
        self.assertEqual(choice['field']['type'], 'select')

    def test_select_field(self):
        form = PageForm1()
        data = form.as_dict()
        self.assertEqual(len(data['children']), 1)
        data = data['children'][0]
        self.assertEqual(data['field']['type'], 'fieldset')
        self.assertEqual(len(data['children']), 3)
        markup = data['children'][1]
        self.assertEqual(markup['field']['type'], 'select')
        options = markup['field']['options']
        self.assertEqual(len(options), 2)
        self.assertTrue(markup['field']['required'])
