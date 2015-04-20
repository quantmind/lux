from lux.utils import test
from lux import forms


class SimpleForm(forms.Form):
    name = forms.CharField()
    email = forms.CharField(required=False)


class FormTests(test.TestCase):

    def test_empty(self):
        form = SimpleForm()
        self.assertFalse(form.instance)
        self.assertFalse(form.manager)
        self.assertFalse(form.model)
        self.assertFalse(form.request)
        self.assertFalse(form.is_bound)

    def test_empty_bound(self):
        form = SimpleForm(data={})
        self.assertFalse(form.instance)
        self.assertFalse(form.manager)
        self.assertFalse(form.model)
        self.assertFalse(form.request)
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())
        self.assertFalse(hasattr(form, 'cleaned_data'))
        self.assertEqual(len(form.errors), 1)

    def test_valid_simple(self):
        form = SimpleForm(data={'name': 'luca'})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.changed)
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertEqual(form.cleaned_data['name'], 'luca')
        form = SimpleForm(data={'name': 'luca', 'email': 'luca@bla.com'})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertTrue(form.changed)

    def test_changed(self):
        form = SimpleForm(data={'name': 'luca', 'email': 'luca@bla.com'})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertTrue(form.changed)

        form = SimpleForm(initial={'name': 'luca', 'email': 'luca@bla.com'},
                          data={'name': 'luca', 'email': ''})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.changed)
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertEqual(form.cleaned_data['email'], '')

    def test_not_changed(self):
        data = {'name': 'luca', 'email': 'luca@bla.com'}
        form = SimpleForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertTrue(form.changed)

        form = SimpleForm(initial=data, data=data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.changed)
        self.assertEqual(form.cleaned_data, data)
