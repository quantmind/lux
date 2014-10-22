from lux.utils import test
from lux import forms


class FieldTests(test.TestCase):

    def test_ChoiceField(self):
        field = forms.ChoiceField()
        self.assertEqual(field.attrs.get('name'), None)
        #
        self.assertEqual(field.options.all(), ())
        attrs = field.getattrs()
        self.assertEqual(attrs['options'], ())
        #
        field = forms.ChoiceField(options=('bla', 'foo'))
        self.assertEqual(field.options.all(), ('bla', 'foo'))
        attrs = field.getattrs()
        self.assertEqual(attrs['options'], ('bla', 'foo'))

    def test_ChoiceFieldOptions(self):
        opts = [{'value': 'a', 'repr': 'foo'},
                {'value': 'b', 'repr': 'hello'}]
        field = forms.ChoiceField(options=opts)
        self.assertEqual(field.options.all(), opts)
