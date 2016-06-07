from lux.utils import test
from lux import forms
from lux.forms import Layout, Fieldset, Submit, Formsets


class SimpleForm(forms.Form):
    name = forms.CharField()
    email = forms.CharField(required=False)


class EmptyFieldsForm(forms.Form):
    users = forms.FormSet(SimpleForm)


class EmailUserForm(EmptyFieldsForm):
    body = forms.CharField()


class FormsetTests(test.TestCase):

    def test_form_class(self):
        self.assertTrue(EmailUserForm.inlines)
        self.assertEqual(len(EmailUserForm.inlines), 1)
        self.assertEqual(EmailUserForm.inlines['users'].form_class,
                         SimpleForm)
        self.assertFalse(EmailUserForm.inlines['users'].is_bound)

    def test_unbound(self):
        form = EmailUserForm()
        self.assertTrue(form.form_sets)
        self.assertFalse(form.is_bound)
        self.assertFalse(form.form_sets['users'].is_bound)
        self.assertEqual(form.form_sets['users'].related_form, form)

    def __test_bound_empty(self):
        form = EmailUserForm(data={'body': 'Hello!'})
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())
        form = EmailUserForm(data={'body': 'Hello!', 'users_num_forms': 0})
        self.assertTrue(form.is_valid())

    def test_serialise(self):
        layout = Layout(EmailUserForm,
                        Fieldset(all=True),
                        Formsets(all=True),
                        Submit('update'))
        self.assertEqual(len(layout.children), 3)
        form = layout()
        data = form.as_dict()
        children = data['children']
        self.assertEqual(len(children), 3)
        self.assertEqual(children[1]['name'], 'users')

    def test_serialise_empty_fields(self):
        layout = Layout(EmptyFieldsForm,
                        Fieldset(all=True),
                        Formsets(all=True),
                        Submit('update'))
        self.assertEqual(len(layout.children), 3)
        form = layout()
        data = form.as_dict()
        children = data['children']
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0]['name'], 'users')
