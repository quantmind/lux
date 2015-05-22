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

    def test_unbound(self):
        form = EmailUserForm()
        self.assertTrue(form.form_sets)
