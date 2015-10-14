from lux.utils import test

from lux.extensions.ui.lib import *     # noqa


class TestMixins(test.TestCase):
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
    border-color: #555;
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
    border: none;
}
''')

    def test_border_bottom(self):
        all = Css()
        b = Border('solid', '#E7E7E7', bottom=px(1))
        self.assertEqual(b.color, '#E7E7E7')
        self.assertEqual(b.width, None)
        self.assertEqual(b.style, 'solid')
        s = all.css('.blax', b)
        text = s.render()
        self.assertEqual(text, '''.blax {
    border-bottom: 1px solid #e7e7e7;
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
        self.assertTrue('.blax:hover' in text)
        self.assertTrue('.blax.hover' in text)
        self.assertFalse('.blax:active' in text)
        self.assertFalse('.blax.active' in text)
        self.assertFalse('border' in text)

    def test_clearfix(self):
        all = Css()
        s = all.css('.bla',
                    Clearfix())
        text = s.render()
        self.assertTrue('.bla:before {' in text)
        self.assertTrue('.bla:after {' in text)

    def test_opacity(self):
        all = Css()
        s = all.css('.bla',
                    Opacity(0.3))
        text = s.render()
        self.assertTrue('opacity' in text)

    def test_inline_block(self):
        all = Css()
        s = all.css('.bla',
                    InlineBlock())
        text = s.render()
        self.assertTrue('display' in text)
        self.assertTrue('zoom' in text)
        self.assertTrue('*display' in text)

    def test_center_block(self):
        all = Css()
        s = all.css('.bla',
                    CenterBlock())
        text = s.render()
        self.assertTrue('display' in text)
        self.assertTrue('margin-left' in text)
        self.assertTrue('margin-right' in text)

    def test_text_overflow(self):
        all = Css()
        s = all.css('.bla',
                    Textoverflow())
        text = s.render()
        self.assertTrue('overflow' in text)
        self.assertTrue('text-overflow' in text)
        self.assertTrue('white-space' in text)

    def test_box_sizing(self):
        all = Css()
        s = all.css('.bla',
                    BoxSizing('content-box'))
        text = s.render()
        self.assertTrue('box-sizing' in text)

    def test_gradient(self):
        all = Css()
        s = all.css('.bla',
                    Gradient('h', '#000', '#fff'))
        text = s.render()
        self.assertTrue('background-color' in text)
        self.assertTrue('background-image' in text)
