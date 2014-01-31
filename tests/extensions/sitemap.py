import lux
from lux.utils import test
from lux.extensions.sitemap import Link


class TestBase(test.TestCase):

    def testLink(self):
        a = Link(icon='collapse', ajax=True)
        self.assertEqual(a.tag, 'a')
        self.assertEqual(str(a), "<a class='ajax'>")
