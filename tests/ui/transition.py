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
