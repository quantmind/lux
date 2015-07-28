from lux.utils import test
from lux.extensions.ui.lib import *


class TestMedia(test.TestCase):

    def test_simple(self):
        all = Css()
        css = all.css
        css('.collapse',
            Transition('height', '0.35s', 'ease'))
        txt = all.render()
        self.assertEqual(txt, '''.collapse {
    -webkit-transition: height 0.35s ease;
       -moz-transition: height 0.35s ease;
         -o-transition: height 0.35s ease;
            transition: height 0.35s ease;
}
''')

    def test_cubic(self):
        all = Css()
        css = all.css
        css('.collapse',
            Transition('transform', '0.35s',
                       'cubic-bezier(0.2, 0.3, 0.25, 0.9)'))
        txt = all.render()
        self.assertEqual(txt, '''.collapse {
    -webkit-transition: transform 0.35s cubic-bezier(0.2,0.3,0.25,0.9);
       -moz-transition: transform 0.35s cubic-bezier(0.2,0.3,0.25,0.9);
         -o-transition: transform 0.35s cubic-bezier(0.2,0.3,0.25,0.9);
            transition: transform 0.35s cubic-bezier(0.2,0.3,0.25,0.9);
}
''')

    def test_two_properties(self):
        all = Css()
        css = all.css
        css('.collapse',
            Transition('opacity, top', '0.3s', 'linear, ease-out'))
        txt = all.render()
        self.assertEqual(txt, '''.collapse {
    -webkit-transition: opacity 0.3s linear, top 0.3s ease-out;
       -moz-transition: opacity 0.3s linear, top 0.3s ease-out;
         -o-transition: opacity 0.3s linear, top 0.3s ease-out;
            transition: opacity 0.3s linear, top 0.3s ease-out;
}
''')

    def test_transform(self):
        all = Css()
        css = all.css
        css('.shift-right',
            Transform(x=px(100)))
        txt = all.render()
        self.assertTrue('translateX(100px)' in txt)

        all = Css()
        css = all.css
        css('.shift-up',
            Transform(y=px(100)))
        txt = all.render()
        self.assertTrue('translateY(100px)' in txt)

        all = Css()
        css = all.css
        css('.shift-up',
            Transform(x=px(50), y=px(100), scale=2))
        txt = all.render()
        self.assertTrue('translate(50px,100px)' in txt)
        self.assertTrue('scale(2)' in txt)
