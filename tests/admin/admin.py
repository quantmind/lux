import inspect

from lux.extensions.admin import admin
from lux.utils import test


class AdminTest(test.TestCase):

    def test_register(self):
        self.assertTrue(inspect.ismodule(admin))
