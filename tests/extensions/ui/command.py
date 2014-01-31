import os

import lux
from lux.utils import test


class CommandTests(test.TestCase):
    config_params = {'EXTENSIONS': ['lux.extensions.base',
                                    'lux.extensions.ui']}

    def testStyle(self):
        command = self.fetch_command('style')
        command(['-t', 'teststyle'])
        self.assertEqual(command.theme, 'teststyle')
        os.remove(command.target)

    def test_style(self):
        command = self.fetch_command('style')
        file = command([])
        self.assertTrue(os.path.isfile(file))
        os.remove(file)

    def test_nodump_style(self):
        command = self.fetch_command('style')
        result = command(['-t', 'teststyle'], dump=False)
        self.assertFalse(os.path.isfile(result))
        self.assertTrue(result)
