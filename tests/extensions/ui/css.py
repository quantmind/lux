import sys
import os

from lux.utils import test
from lux.extensions.ui.lib import *


class TestCSS(test.TestCase):

    def testSimple(self):
        # the variable does not exist
        all = Css()
        c = all.css('#random', margin=cssv.skjncdfcd)
        self.assertFalse(c.attributes)
        self.assertEqual(c.parent, css('body'))


class TestMixins(test.TestCase):
    '''Test the simple Mixins'''

    def testRadius(self):
        s = css('.bla', Radius(px(5)))
        text = s.render()
        self.assertEqual(text, '''.bla {
    -webkit-border-radius: 5px;
       -moz-border-radius: 5px;
            border-radius: 5px;
}
''')

    def testRadiusSpacing(self):
        ra = Radius(spacing('5px', 0))
        s = css('.bla', ra)
        text = s.render()
        self.assertEqual(text, '''.bla {
    -webkit-border-radius: 5px 0;
       -moz-border-radius: 5px 0;
            border-radius: 5px 0;
}
''')

    def testRadiusVariable(self):
        r = Symbol('x', spacing(px(5), 0))
        s = css('.bla', Radius(r))
        text = s.render()
        self.assertEqual(text, '''.bla {
    -webkit-border-radius: 5px 0;
       -moz-border-radius: 5px 0;
            border-radius: 5px 0;
}
''')

    def testBorder(self):
        b = Border(color='#555')
        self.assertEqual(b.color, '#555')
        s = css('.bla', b)
        text = s.render()
        self.assertEqual(text, '''.bla {
    border: 1px solid #555;
}
''')

    def testBorderVariables(self):
        c = Variables()
        c.border.color = '#222'
        c.border.style = 'dotted'
        c.border.width = None
        b = Border(**c.border.params())
        s = css('.bla', b)
        text = s.render()
        self.assertEqual(text, '''.bla {
    border: 1px dotted #222;
}
''')

    def testBorderVariables2(self):
        c = Variables()
        c.border.color = color('222')
        c.border.style = 'dotted'
        c.border.width = None
        b = Border(**c.border.params())
        s = css('.bla', b)
        text = s.render()
        self.assertEqual(text, '''.bla {
    border: 1px dotted #222;
}
''')

    def testBoxShadow(self):
        s = css('.bla',
                Shadow('10px 10px 5px #888'),
                display='block')
        text = s.render()
        r = '''
    -webkit-box-shadow: 10px 10px 5px #888;
       -moz-box-shadow: 10px 10px 5px #888;
            box-shadow: 10px 10px 5px #888;'''
        self.assertTrue(r in text)

    def test_fixtop(self):
        s = css('.foo',
                fixtop(3000))
        text = s.render()
        r = '''
    left: 0;
    top: 0;
    right: 0;
    position: fixed;
    z-index: 3000;'''
        self.assertTrue(r in text)

    def test_clickable(self):
        s = css('.click',
                Clickable(cursor=None))
        self.assertEqual(s.render(), '')
        s = css('.click', Clickable(default=bcd(color=color('#333'))))
        self.assertEqual(s.render(), '''.click {
    cursor: pointer;
    color: #333;
}
''')
        s = css('.click', Clickable(default=bcd(color='#333333'),
                                    hover=bcd(color='#000000'),
                                    active=bcd(color='#222222')))
        text = s.render()
        self.assertEqual(text, '''.click {
    cursor: pointer;
    color: #333;
}

.click:hover {
    color: #000;
}

.click.%s {
    color: #000;
}

.click:active {
    color: #222;
}

.click.%s {
    color: #222;
}
''' % (classes.state_hover, classes.state_active))


class TestGradient(test.TestCase):

    def test_vgradient(self):
        s = css('.bla',
                gradient(('v', '#ffffff', '#f5f5f5')),
                display='block')
        text = s.render()
        r = '''
    background-color: #f5f5f5;
    background-image: -moz-linear-gradient(top, #ffffff, #f5f5f5);
    background-image: -ms-linear-gradient(top, #ffffff, #f5f5f5);
    background-image: -webkit-gradient(linear, 0 0, 0 100%, from(#ffffff), to(#f5f5f5));
    background-image: -webkit-linear-gradient(top, #ffffff, #f5f5f5);
    background-image: -o-linear-gradient(top, #ffffff, #f5f5f5);
    background-image: linear-gradient(top, #ffffff, #f5f5f5);
    background-repeat: repeat-x;
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#ffffff', endColorstr='#f5f5f5', GradientType=0);'''
        self.assertTrue(r in text)

    def testColor(self):
        d = {}
        g = gradient('#222')
        g(d)
        self.assertEqual(d['background'], color('#222'))

    def testBadGradient(self):
        d = {}
        self.assertRaises(ValueError, lambda: gradient(5)(d))
        self.assertRaises(ValueError, lambda: gradient((5,))(d))
        self.assertRaises(ValueError, lambda: gradient((5, 4))(d))
        self.assertRaises(ValueError, lambda: gradient((4, 5, 6, 7))(d))


class TestBCD(test.TestCase):

    def testObject(self):
        b = bcd()
        self.assertFalse(b.color)
        self.assertFalse(b.text_decoration)
        self.assertFalse(b.text_shadow)

    def testCss(self):
        c = css('#testbcd', bcd(color='#444'))
        self.assertTrue(c.children)
        text = c.render()
        self.assertEqual(text, '''#testbcd {
    color: #444;
}
''')


class TestNavigation(test.TestCase):

    def testMeta(self):
        nav = horizontal_navigation()
        self.assertEqual(nav.float, 'left')
        nav = horizontal_navigation(float='bla')
        self.assertEqual(nav.float, 'left')
        nav = horizontal_navigation(float='right')
        self.assertEqual(nav.float, 'right')

    def testRender(self):
        nav = css('.nav', horizontal_navigation())
        text = nav.render()
        self.assertTrue(text)


class TestTopBar(test.TestCase):

    def test_meta(self):
        tb = css('.topbar', topbar())
        text = tb.render()
        self.assertTrue(text)


class TestUi(test.TestCase):

    def testHorizontalDl(self):
        dl = css('body').children['.%s' % classes.dl_horizontal]
        self.assertEqual(len(dl), 1)
        dl = dl[0]
        text = dl.render()
        self.assertTrue('.%s dt' % classes.dl_horizontal in text)
