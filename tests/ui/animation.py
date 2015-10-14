from lux.utils import test
from lux.extensions.ui.lib import *     # noqa


class TestAnimation(test.TestCase):

    def test_simple(self):
        all = Css()
        css = all.css
        css('.collapse',
            Animation('fade', '1s', 'linear'))
        txt = all.render()
        self.assertTrue('animation-timing-function: linear' in txt)
