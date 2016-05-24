from enum import Enum
import json
from datetime import date, datetime

import pytz

from lux.utils import test
from lux import forms


class TestEnum(Enum):
    opt1 = '1'
    opt2 = '2'


class SimpleForm(forms.Form):
    name = forms.CharField(minlength=2, maxlength=30)
    email = forms.CharField(required=False)
    rank = forms.IntegerField(required=False)
    dt = forms.DateField(required=False)
    timestamp = forms.DateTimeField(required=False)
    enum_field = forms.ChoiceField(required=False, options=TestEnum)


class PageForm(forms.Form):
    """From an legacy extension"""
    path = forms.CharField(required=False)
    title = forms.CharField()
    description = forms.TextField(required=False)
    published = forms.BooleanField(required=False)
    layout = forms.JsonField(text_edit=json.dumps({'mode': 'json'}))

    def clean_layout(self, value):
        if not isinstance(value, dict):
            raise forms.ValidationError('Layout must be a dictionary')
        layout = {}
        if 'components' in value:
            components = value['components']
            if not isinstance(components, list):
                raise forms.ValidationError('componets must be a list')
            layout['components'] = components
        if 'rows' in value:
            rows = value['rows']
            if not isinstance(rows, list):
                raise forms.ValidationError('rows must be a list')
            layout['rows'] = rows
        return layout


class FailForm(SimpleForm):

    def clean(self):
        raise forms.ValidationError('wrong data')


class FormTests(test.TestCase):

    def test_empty(self):
        form = SimpleForm()
        self.assertFalse(form.request)
        self.assertFalse(form.is_bound)

    def test_empty_bound(self):
        form = SimpleForm(data={})
        self.assertFalse(form.request)
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())
        self.assertFalse(hasattr(form, 'cleaned_data'))
        self.assertEqual(len(form.errors), 1)

    def test_valid_simple(self):
        form = SimpleForm(data={'name': 'luca'})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.changed)
        self.assertEqual(len(form.cleaned_data), 1)
        self.assertEqual(form.cleaned_data['name'], 'luca')
        form = SimpleForm(data={'name': 'luca', 'email': 'luca@bla.com'})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertTrue(form.changed)

    def test_valid_simple_none(self):
        form = SimpleForm(data={'name': 'luca', 'rank': None})
        self.assertTrue(form.is_valid(exclude_missing=True))
        self.assertTrue(form.changed)
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertEqual(form.cleaned_data['name'], 'luca')
        self.assertTrue('rank' in form.cleaned_data)
        self.assertEqual(form.cleaned_data['rank'], None)

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
        self.assertTrue('email' in form.cleaned_data)
        self.assertTrue(form.cleaned_data['email'] is None)

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
        form_class = forms.create_form('TestForm',
                                       forms.CharField('name'),
                                       forms.CharField('surname'))
        self.assertEqual(form_class.__name__, 'TestForm')

    def test_clean_fail(self):
        data = {'name': 'luca', 'email': 'luca@bla.com'}
        form = FailForm(data=data)
        self.assertRaises(forms.FormError, lambda: form.data)
        self.assertFalse(form.is_valid())
        self.assertValidationError(form.tojson(), '', 'wrong data')
        self.assertEqual(len(form.data), 2)

    def test_charfield_error(self):
        class failconvert:
            def __str__(self):
                raise Exception

        form = SimpleForm(data=dict(name=failconvert()))
        self.assertFalse(form.is_valid())
        self.assertValidationError(form.tojson(), 'name',
                                   'Invalid value')

    def test_integer_field(self):
        form = SimpleForm(data=dict(name='luca', rank='1'))
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertEqual(form.cleaned_data['rank'], 1)
        #
        form = SimpleForm(data=dict(name='luca', rank=1.2))
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertEqual(form.cleaned_data['rank'], 1)
        #
        form = SimpleForm(data=dict(name='luca', rank='1,045'))
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertEqual(form.cleaned_data['rank'], 1045)

    def test_integer_field_error(self):
        form = SimpleForm(data=dict(name='luca', rank='foo'))
        self.assertFalse(form.is_valid())
        self.assertValidationError(form.tojson(), 'rank',
                                   'Not a valid number')

    def test_date_field(self):
        dt = date.today()
        form = SimpleForm(data=dict(name='luca', dt=dt.isoformat()))
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertEqual(form.cleaned_data['dt'], dt)
        #
        form = SimpleForm(data=dict(name='luca', dt=dt.strftime("%d %B %Y")))
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertEqual(form.cleaned_data['dt'], dt)

    def test_date_field_error(self):
        form = SimpleForm(data=dict(name='luca', dt='xyz'))
        self.assertFalse(form.is_valid())
        self.assertValidationError(form.tojson(), 'dt',
                                   'Not a valid date')

    def test_datetime_field(self):
        dt = datetime.now()
        form = SimpleForm(data=dict(name='luca', timestamp=dt.isoformat()))
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertEqual(form.cleaned_data['timestamp'], pytz.utc.localize(dt))

    def test_datetime_field_error(self):
        form = SimpleForm(data=dict(name='luca', timestamp='xyz'))
        self.assertFalse(form.is_valid())
        self.assertValidationError(form.tojson(), 'timestamp',
                                   'Not a valid date')

    def test_enum_field(self):
        form = SimpleForm(data=dict(name='luca', enum_field='opt1'))
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertEqual(form.cleaned_data['enum_field'], 'opt1')

    def test_enum_field_error(self):
        form = SimpleForm(data=dict(name='luca', enum_field='optfail'))
        self.assertFalse(form.is_valid())
        self.assertValidationError(form.tojson(), 'enum_field',
                                   'optfail is not a valid choice')

    def test_clean_field_in_form(self):
        form = PageForm(data=dict(title='Just a test',
                                  layout=json.dumps({})))
        self.assertTrue(form.is_valid(True))
        #
        form = PageForm(data=dict(title='Just a test',
                                  layout=json.dumps([1, 2])))
        self.assertFalse(form.is_valid(True))
        self.assertValidationError(form.tojson(), 'layout',
                                   'Layout must be a dictionary')
        #
        form = PageForm(data=dict(title='Just a test',
                                  layout=json.dumps({'foo': 5})))
        self.assertTrue(form.is_valid(True))
        self.assertEqual(form.cleaned_data['layout'], {})

    def test_minlength(self):
        form = SimpleForm(data=dict(name='l'))
        self.assertFalse(form.is_valid())
        self.assertValidationError(form.tojson(), 'name',
                                   'too short')

    def test_maxlength(self):
        form = SimpleForm(data=dict(name=50*'l'))
        self.assertFalse(form.is_valid())
        self.assertValidationError(form.tojson(), 'name',
                                   'too long')

    def test_form_message(self):
        form = PageForm(data={})
        self.assertFalse(form.exclude_missing)
        self.assertFalse(form.is_valid())
        msg = form.message()
        self.assertTrue(msg.startswith('ERROR: '))
