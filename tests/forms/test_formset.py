from lux.utils import test
from lux import forms
from lux.forms import Layout, Fieldset, Inline, Submit


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

    def test_serialise(self):
        layout = Layout(EmailUserForm,
                        Fieldset('body'),
                        Inline('users'),
                        Submit('update'))
        self.assertEqual(len(layout.children), 3)
        form = layout()
        data = form.as_dict()
        children = data['children']
        self.assertEqual(len(children), 3)
        self.assertEqual(children[1]['name'], 'users')

    def test_serialise_empty_fields(self):
        layout = Layout(EmptyFieldsForm,
                        Fieldset(empty=True, name='foo'),
                        Inline('users'),
                        Submit('update'))
        self.assertEqual(len(layout.children), 3)
        form = layout()
        data = form.as_dict()
        children = data['children']
        self.assertEqual(len(children), 3)
        self.assertEqual(children[0]['name'], 'foo')
        self.assertEqual(children[1]['name'], 'users')

    def test_validation_empty_formset(self):
        form = EmailUserForm(data={'body': 'fooo'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, {'body': 'fooo'})

    def test_validation_fail(self):
        form = EmailUserForm(data={'body': 'fooo', 'users': 'foo'})
        self.assertFalse(form.is_valid())

    def test_validation_fail2(self):
        users = [
            {'email': 'foo@gmail.com'}
        ]
        form = EmailUserForm(data={'body': 'fooo', 'users': users})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['users']), 1)

    def test_validation(self):
        users = [
            {'name': 'foo', 'email': 'foo@gmail.com'},
            {'name': 'bla', 'email': 'bla@gmail.com'}
        ]
        form = EmailUserForm(data={'body': 'fooo',
                                   'users': users})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['body'], 'fooo')
        self.assertEqual(len(form.cleaned_data['users']), 2)
        self.assertTrue(form.is_valid())
