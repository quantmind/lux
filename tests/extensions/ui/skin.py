__test__ = False
from lux.utils import test
from lux.extensions.ui.lib import *


class TestSkins(test.TestCase):

    def __test_border_width(self):
        all = self.root()
        css = all.css
        b = spacing(0, 0, 0, px(1))
        bla = css('.bla', Skin(border_width=b))
        self.assertEqual(bla, all.children.get('.bla')[-1])
        self.assertTrue(bla)
        self.assertEqual(len(bla.children), 1)
        skin = list(bla.children.values())[0][0]
        self.assertEqual(skin.border_width, b)

    def test_default_skin(self):
        r = self.root(skins=True)
        bla = r.css('.bla', Skin(clickable=True))
        txt = r.render()
        self.assertTrue('.bla {' in txt)
        self.assertTrue('.bla.primary {' in txt)

    def __test_zen_skin(self):
        all = self.all()
        bla = all.css('.bla', Skin(clickable=True))
        txt = bla.render()
        self.assertTrue('.bla.zen {' in txt)
