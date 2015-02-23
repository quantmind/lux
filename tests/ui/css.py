import sys
import os

from lux.utils import test
from lux.extensions.ui.lib import *


class TestCSS(test.TestCase):

    def test_simple(self):
        # the variable does not exist
        all = Css()
        css = all.css
        vars = all.variables
        c = css('#random', margin=vars.skjncdfcd)
        self.assertFalse(c.attributes)
        self.assertEqual(c.parent, all)

    def test_radius(self):
        css = Css().css
        s = css('.bla', Radius(px(5)))
        text = s.render()
        self.assertEqual(text, '''.bla {
    -webkit-border-radius: 5px;
       -moz-border-radius: 5px;
            border-radius: 5px;
}
''')

    def testRadiusSpacing(self):
        all = Css()
        css = all.css
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
        all = Css()
        css = all.css
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
        all = Css()
        css = all.css
        b = Border(color='#555')
        self.assertEqual(b.color, '#555')
        s = css('.bla', b)
        text = s.render()
        self.assertEqual(text, '''.bla {
    border-color: #555;
}
''')

    def testBorderVariables(self):
        all = Css()
        css = all.css
        c = Variables()
        c.border.color = '#222'
        c.border.style = 'dotted'
        c.border.width = None
        b = Border(**c.border.params())
        s = css('.bla', b)
        text = s.render()
        self.assertEqual(text, '''.bla {
    border-style: dotted;
    border-color: #222;
}
''')

    def testBorderVariables2(self):
        all = Css()
        css = all.css
        c = Variables()
        c.border.color = color('222')
        c.border.style = 'dotted'
        c.border.width = px(2)
        b = Border(**c.border.params())
        s = css('.bla', b)
        text = s.render()
        self.assertEqual(text, '''.bla {
    border: 2px dotted #222;
}
''')

    def testBoxShadow(self):
        all = Css()
        css = all.css
        s = css('.bla',
                Shadow(10, 10, 5, color='#888'),
                display='block')
        text = s.render()
        r = '''
    -webkit-box-shadow: 10px 10px 5px #888;
       -moz-box-shadow: 10px 10px 5px #888;
            box-shadow: 10px 10px 5px #888;'''
        self.assertTrue(r in text)

    def test_fixtop(self):
        all = Css()
        css = all.css
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

class f:

    def test_clickable(self):
        all = Css()
        css = all.css
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

    # Gradient
    def test_vgradient(self):
        all = Css()
        css = all.css
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
