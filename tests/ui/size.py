from lux.utils import test
from lux.extensions.ui.lib import *     # noqa


class TestSize(test.TestCase):

    def make(self):
        return px(18)

    def testPX(self):
        a = px(14)
        self.assertEqual(str(a), '14px')
        self.assertEqual(a._value, 14)
        self.assertEqual(str(a+2), '16px')
        self.assertEqual(str(a), '14px')
        self.assertRaises(TypeError, px, 'cjhbc')

    def testPC(self):
        a = pc(80)
        self.assertEqual(str(a), '80%')

    def testEM(self):
        a = em(1.2)
        self.assertEqual(str(a), '1.2em')

    def testMultiply(self):
        a = px(15)
        b = 2*a
        self.assertEqual(b.unit, 'px')
        self.assertEqual(str(b), '30px')
        b = 1.5*a
        self.assertEqual(b.unit, 'px')
        self.assertEqual(str(b), '%dpx' % round(1.5*15))
        self.assertRaises(TypeError, lambda: a*b)

    def __testDivide(self):
        # TODO: fix this for python 2
        a = px(15)
        b = a/2
        r = round(0.5*15)
        self.assertEqual(b.unit, 'px')
        self.assertEqual(b._value, r)
        self.assertEqual(str(b), '%dpx' % r)
        b = a/3
        r = round(15/3.)
        self.assertEqual(b.unit, 'px')
        self.assertEqual(b._value, r)
        self.assertEqual(str(b), '%dpx' % r)
        self.assertRaises(TypeError, lambda: a/b)

    def testVariable(self):
        v = Variables()
        v.size = px(5)
        self.assertEqual(str(v.size), '5px')
        self.assertEqual(px(v.size), v.size)

    def test_px_spacing(self):
        a = spacing(px(5))
        self.assertEqual(a.top, px(5))
        self.assertEqual(a.right, px(5))
        self.assertEqual(a.bottom, px(5))
        self.assertEqual(a.left, px(5))
        self.assertEqual(str(a), '5px')
        self.assertEqual(a.unit, 'px')
        a = spacing(px(5), px(2))
        self.assertEqual(a.top, px(5))
        self.assertEqual(a.right, px(2))
        self.assertEqual(a.bottom, px(5))
        self.assertEqual(a.left, px(2))
        self.assertEqual(str(a), '5px 2px')
        a = spacing(px(5), px(2), px(10))
        self.assertEqual(str(a.top), '5px')
        self.assertEqual(str(a.right), '2px')
        self.assertEqual(str(a.bottom), '10px')
        self.assertEqual(str(a.left), '2px')
        self.assertEqual(str(a), '5px 2px 10px')
        a = spacing(px(5), px(2), px(10), px(7))
        self.assertEqual(a.top, px(5))
        self.assertEqual(a.right, px(2))
        self.assertEqual(a.bottom, px(10))
        self.assertEqual(a.left, px(7))
        self.assertEqual(str(a), '5px 2px 10px 7px')

    def test_simple_spacing(self):
        a = spacing(5)
        self.assertEqual(a.top, px(5))
        self.assertEqual(a.right, px(5))
        self.assertEqual(a.bottom, px(5))
        self.assertEqual(a.left, px(5))
        self.assertEqual(str(a), '5px')
        a = spacing(5, 4)
        self.assertEqual(a.top, px(5))
        self.assertEqual(a.right, px(4))
        self.assertEqual(a.bottom, px(5))
        self.assertEqual(a.left, px(4))
        self.assertEqual(str(a), '5px 4px')
        # mix and match
        a = spacing(5, em(1.1), pc(2), px(2))
        self.assertEqual(a.top, px(5))
        self.assertEqual(a.right, em(1.1))
        self.assertEqual(a.bottom, pc(2))
        self.assertEqual(str(a.left), '2px')
        self.assertEqual(str(a), '5px 1.1em 2% 2px')

    def __testBadSpacing(self):
        # TODO: fix this
        self.assertRaises(TypeError, spacing, 5, 4, 5, 6, 7)
        self.assertRaises(TypeError, spacing, 5, 'bla')
        self.assertRaises(TypeError, spacing, 5, None)
        sp = spacing(5)
        self.assertEqual(sp, '5px')

    def test_lazy_spacing(self):
        v = Symbol('bla', spacing(5))
        sp = v*2
        self.assertEqual(str(sp), '10px')

    def test_spacing_bad_variable(self):
        v = Variables()
        v.bla = spacing(5, 4)
        s = spacing(v.bla, px(3))
        self.assertRaises(TypeError, str, s)

    def test_spacing_multiply(self):
        a = spacing(5, 10)
        b = 0.5*a
        self.assertEqual(b.left, 0.5*a.left)
        self.assertEqual(b.top, 0.5*a.top)

    def test_spacing_auto(self):
        a = spacing(px(60), 'auto')
        self.assertEqual(str(a.left), 'auto')

    def test_spacing_variable(self):
        v = Variables()
        v.space = px(250)
        s = spacing(0, 0, 0, v.space)
        self.assertIsInstance(s.left, Variable)
        self.assertEqual(str(s), '0 0 0 250px')
        v.space = px(200)
        self.assertEqual(str(s), '0 0 0 200px')
