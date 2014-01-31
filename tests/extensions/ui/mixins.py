from lux.extensions.ui.lib import *

from . import vars


class TestMixins(vars.TestCase):
    '''Test the simple mixins'''
    def testNotImplemented(self):
        m = Mixin()
        m(None)

    def test_border_color(self):
        all = Css()
        b = Border(color='#555')
        self.assertEqual(b.color, '#555')
        s = all.css('.bla', b)
        self.assertEqual(len(s.children), 1)
        text = s.render()
        self.assertEqual(text, '''.bla {
    border: 1px solid #555;
}
''')

    def test_border_none(self):
        all = Css()
        b = Border(width=0, style='none')
        self.assertEqual(b.color, None)
        self.assertEqual(b.width, 0)
        self.assertEqual(b.style, 'none')
        s = all.css('.blax', b)
        text = s.render()
        self.assertEqual(text, '''.blax {
    border: 0 none;
}
''')

    def test_clickable(self):
        all = Css()
        b = Clickable(default={'background': '#111'},
                      hover={'background': '#555'})
        self.assertTrue(b.default)
        self.assertTrue(b.default.background)
        self.assertFalse(b.default.color)
        self.assertFalse(b.default.border)
        self.assertTrue(b.hover)
        self.assertFalse(b.active)
        s = all.css('.blax', b)
        text = s.render()
        self.assertTrue('.blax {' in text)
        self.assertTrue('.blax:hover {' in text)
        self.assertTrue('.blax.hover {' in text)
        self.assertFalse('.blax:active {' in text)
        self.assertFalse('.blax.active {' in text)
        self.assertFalse('border' in text)

    def test_clearfix(self):
        all = Css()
        s = all.css('.bla',
                    Clearfix(),
                    display='block')
        text = s.render()
        self.assertTrue('*zoom: 1;' in text)
        self.assertEqual(text, '''.bla {
    display: block;
    *zoom: 1;
}

.bla:before {
    content: "";
    display: table;
}

.bla:after {
    content: "";
    display: table;
    clear: both;
}
''')
