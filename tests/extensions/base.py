import lux
from lux.utils import test


class TestBase(test.TestCase):
        
    def test_doc(self):
        app = self.application()
        self.assertEqual(app.config['MEDIA_URL'], '/static/')