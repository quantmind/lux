import lux
from lux.utils import test
from lux.extensions import ui


class TestUI(test.TestCase):

    def testTabs(self):
        tabs = ui.Tabs()
        self.assertEqual(tabs.tag, 'div')
        self.assertTrue(tabs.hasClass('tabs'))
        tabs.append('bla')
        self.assertEqual(len(tabs.children), 2)
        tabs.append('foo')
        self.assertEqual(len(tabs.children), 3)
        self.assertRaises(ValueError, tabs.append, ['bla'])
        tabs.append(['pippo', 'pluto'])
        self.assertEqual(len(tabs.children), 4)
