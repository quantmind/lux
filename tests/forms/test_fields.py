from enum import Enum
import json

from lux.utils import test
from lux import forms


class TestEnum(Enum):
    opt1 = '1'
    opt2 = '2'


class FieldTests(test.TestCase):

    def test_ChoiceField(self):
        field = forms.ChoiceField()
        self.assertEqual(field.attrs.get('name'), None)
        #
        self.assertEqual(field.options.all(), [])
        attrs = field.getattrs()
        self.assertEqual(attrs['options'], [])
        #
        field = forms.ChoiceField(options=('bla', 'foo'))
        self.assertEqual(field.options.all(), ['bla', 'foo'])
        attrs = field.getattrs()
        self.assertEqual(attrs['options'], ['bla', 'foo'])
        #
        self.assertEqual(repr(field), 'ChoiceField')

    def test_ChoiceField_Options(self):
        opts = [{'value': 'a', 'repr': 'foo'},
                {'value': 'b', 'repr': 'hello'}]
        field = forms.ChoiceField(options=opts)
        self.assertEqual(field.options.all(), opts)
        self.assertEqual(field.options.get_initial(), 'a')

    def test_options(self):
        opts = ('uno', 'due', 'tre')
        field = forms.ChoiceField(options=opts)
        self.assertEqual(field.options.all(), list(opts))
        self.assertEqual(field.options.get_initial(), 'uno')

    def test_options_call(self):
        result = [(1, 'uno'), (2, 'due'), (3, 'tre')]

        def opts(form):
            self.assertEqual(form, None)
            return result

        field = forms.ChoiceField('foo', options=opts)
        self.assertEqual(field.options.all(), result)
        #
        self.assertEqual(repr(field), 'foo')

    def test_ChoiceField_Enum(self):
        field = forms.ChoiceField(options=TestEnum)
        self.assertEqual(field.attrs.get('name'), None)
        #
        self.assertEqual(field.options.all(), ['opt1', 'opt2'])
        attrs = field.getattrs()
        self.assertEqual(attrs['options'], ['opt1', 'opt2'])

    def test_JsonField(self):
        field = forms.JsonField()

        value = {'test': '????'}
        t = type(value)
        json_val = json.dumps(value)

        result = field._clean(json_val, None)

        self.assertEqual(type(result), t)

    def test_JsonField_raises(self):
        field = forms.JsonField()
        value = 'string'

        with self.assertRaises(forms.ValidationError):
            field._clean(value, None)
