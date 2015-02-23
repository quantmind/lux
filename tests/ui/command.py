import os

import lux
from lux.utils import test


class CommandTests(test.TestCase):
    config_file = 'luxpy.ui'
    config_params = {'EXTENSIONS': ['lux.extensions.base',
                                    'lux.extensions.ui']}

    def test_style_cssfile(self):
        command = self.fetch_command('style')
        targets = command(['--cssfile', 'teststyle'])
        self.assertEqual(len(targets), 1)
        self.assertTrue(os.path.isfile(targets[0]))
        self.assertEqual(targets[0], 'teststyle.css')
        os.remove(targets[0])

    def test_style(self):
        command = self.fetch_command('style')
        targets = command([])
        self.assertEqual(len(targets), 1)
        self.assertTrue(os.path.isfile(targets[0]))
        self.assertEqual(targets[0], 'ui.css')
        os.remove(targets[0])

    def test_nodump_style(self):
        command = self.fetch_command('style')
        result = command(['--cssfile', 'teststyle'], dump=False)
        self.assertFalse(os.path.isfile(result))
        self.assertTrue(result)
