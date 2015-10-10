from lux.extensions.ui import *     # noqa
from lux.utils import test


class TestVariables(test.TestCase):

    def root(self, skins=False):
        all = Css()
        self.assertEqual(all.tag, None)
        self.assertEqual(all.code, 'ROOT')
        self.assertEqual(list(all.variables), [])
        if skins:
            add_skins(all)
        return all

    def all(self):
        all = self.root()
        add_css(all)
        return all

    def test_lazy_from_sum(self):
        vars = Variables()
        vars.size = px(100)
        val = vars.size + 1
        self.assertIsInstance(val, Variable)
        self.assertEqual(val.value(), '101px')
        vars.size = 200
        self.assertEqual(val.value(), 201)

    def test_lazy_from_mult_sum(self):
        vars = Variables()
        vars.size = px(100)
        val = 2*vars.size + 1
        self.assertIsInstance(val, Variable)
        self.assertEqual(val.value(), '201px')
        vars.size = 200
        self.assertEqual(val.value(), 401)

    def testNotImplemented(self):
        v = Variable()
        self.assertRaises(NotImplementedError, v.value)
        self.assertRaises(NotImplementedError, str, v)

    def testSimpleVariable(self):
        v = Symbol('bla')
        self.assertEqual(v.value(), None)
        self.assertEqual(str(v), '')
        v = Symbol('bla', px(2))
        self.assertEqual(v.value(), px(2))
        self.assertEqual(str(v), '2px')

    def testOperation(self):
        v = Symbol('bla', px(3))
        v2 = v + px(1)
        self.assertTrue(isinstance(v, Variable))
        self.assertEqual(v2.value(), '4px')
        # Now change the v symbol
        v.value(px(2))
        self.assertEqual(v2.value(), '3px')

    def test_symbol(self):
        v = Symbol('bla', 3)
        self.assertEqual(v.name, 'bla')
        self.assertEqual(v.value(), 3)

    def test_right_subtract(self):
        vars = Variables()
        vars.v = px(8)
        v2 = 30 - vars.v
        self.assertEqual(str(v2), '22px')
        self.assertIsInstance(v2, Variable)

    def test_unspecified(self):
        all = Css()
        vars = all.variables
        vars.color = None
        s = all.css('a', color=vars.color)
        text = s.render()
        self.assertFalse(text)
        s = all.css('a', color=vars.color)
        vars.color = color('#333')
        text = s.render()
        self.assertEqual(text, '''a {
    color: #333;
}
''')
