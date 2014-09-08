import os
import io
import shutil
from os import path

import lux
from lux.utils import test


class AppTests(test.TestCase):

    def test_app(self):
        app = self.application()
        self.assertFalse(app.meta.script)
        self.assertEqual(len(app.meta.argv), 2)
