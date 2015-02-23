from lux.utils import test
from lux import forms


class TestAForm1(forms.Form):
    name = forms.CharField()

    angular = forms.AngularLayout()

    angular2 = forms.AngularLayout(
        forms.AngularFieldset(all=True),
        forms.AngularSubmit('done'))


class PageForm(forms.Form):
    url = forms.CharField()
    markup = forms.ChoiceField(options=('bla', 'foo'))
    body = forms.CharField(type='textarea', required=False)


class FormAngularLayoutTests(test.TestCase):

    def test_layout_class(self):
        angular = TestAForm1.angular
        self.assertTrue(isinstance(angular, forms.AngularLayout))
        self.assertTrue(angular.form_class)
        self.assertEqual(angular.form_class, TestAForm1)
        self.assertEqual(len(angular.children), 1)

    def test_form_data(self):
        form = TestAForm1()
        data = form.angular.as_dict()
        self.assertEqual(len(data), 2)
        self.assertEqual(data['field']['type'], 'form')
        self.assertEqual(len(data['children']), 1)

    def test_render_form(self):
        form = TestAForm1()
        html = form.angular.as_form()
        self.assertEqual(html.tag, 'lux-form')
        self.assertEqual(len(html.children), 1)

    def test_render_form_width_button(self):
        form = TestAForm1()
        data = form.angular2.as_dict()
        self.assertEqual(len(data['children']), 2)

    def test_textarea(self):
        form = PageForm()
        data = form.layout.as_dict()
        self.assertEqual(len(data['children']), 1)
        data = data['children'][0]
        self.assertEqual(data['field']['type'], 'fieldset')
        self.assertEqual(len(data['children']), 3)
        textarea = data['children'][2]
        self.assertEqual(textarea['field']['type'], 'textarea')
        choice = data['children'][1]
        self.assertEqual(choice['field']['type'], 'select')

    def __test_layout_create(self):
        class TestForm(forms.Form):
            name = forms.CharField()
        form = TestForm()
        html = form.layout()
        self.assertEqual(html.tag, 'form')
        txt = html.render()
        self.assertTrue(txt)
