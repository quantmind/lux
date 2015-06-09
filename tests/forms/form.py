from lux.utils import test
from lux import forms


class SimpleForm(forms.Form):
    name = forms.CharField()
    email = forms.CharField(required=False)


class FailForm(SimpleForm):

    def clean(self):
        raise forms.ValidationError('wrong data')


class FormTests(test.TestCase):

    def test_empty(self):
        form = SimpleForm()
        self.assertFalse(form.instance)
        self.assertFalse(form.request)
        self.assertFalse(form.is_bound)

    def test_empty_bound(self):
        form = SimpleForm(data={})
        self.assertFalse(form.instance)
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

    def test_make_form(self):
        form_class = forms.MakeForm('TestForm',
                                    forms.CharField('name'),
                                    forms.CharField('surname'))
        self.assertEqual(form_class.__name__, 'TestForm')

    def test_clean_fail(self):
        data = {'name': 'luca', 'email': 'luca@bla.com'}
        form = FailForm(data=data)
        self.assertRaises(forms.FormError, lambda: form.data)
        self.assertFalse(form.is_valid())
        result = form.tojson()
        self.assertTrue(result['error'])
        self.assertFalse(result['success'])
        self.assertEqual(len(result['messages']), 1)
        messages = result['messages'][forms.FORMKEY]
        self.assertEqual(len(messages), 1)
        message = messages[0]
        self.assertEqual(message['message'], 'wrong data')
        self.assertTrue(message['error'])
        self.assertEqual(len(form.data), 2)

    def test_charfield_error(self):
        class failconvert:
            def __str__(self):
                raise Exception

        form = SimpleForm(data=dict(name=failconvert()))
        self.assertFalse(form.is_valid())
        result = form.tojson()
        self.assertEqual(result['messages']['name'][0]['message'],
                         'Invalid value')
