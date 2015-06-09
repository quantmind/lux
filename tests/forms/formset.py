from lux.utils import test
from lux import forms


class SimpleForm(forms.Form):
    name = forms.CharField()
    email = forms.CharField(required=False)


class EmailUserForm(forms.Form):
    body = forms.CharField()

    users = forms.FormSet(SimpleForm)


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

    def test_bound_empty(self):
        form = EmailUserForm(data={'body': 'Hello!'})
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())
        form = EmailUserForm(data={'body': 'Hello!', 'users_num_forms': 0})
        self.assertTrue(form.is_valid())
