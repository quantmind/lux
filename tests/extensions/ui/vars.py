from lux.utils import test
from lux.extensions.ui.lib import *


class TestCase(test.TestCase):

    def all(self):
        from lux.extensions import ui
        from lux.extensions import cms
        all = Css()
        self.assertEqual(all.tag, None)
        self.assertEqual(all.code, 'ROOT')
        self.assertEqual(list(all.variables), [])
        ui.add_css(all)
        return all


class TestVariables(TestCase):

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


class TestSize(TestCase):

    def test_symbol(self):
        v = Symbol('bla', 3)
        self.assertEqual(v.name, 'bla')
        self.assertEqual(v.value(), 3)
