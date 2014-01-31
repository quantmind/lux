from lux.extensions.cms import add_css
from lux.extensions.cms.ui import Gridfluid, Css

from tests.extensions import cms as test


class TestGrid(test.TestCase):

    def __test_grid940(self):
        all = Css()
        g = Gridfluid(24)
        self.assertEqual(g.columns, 24)
        elem = all.css('body', g)

    def __test_ui(self):
        all = Css()
        add_css(all)
