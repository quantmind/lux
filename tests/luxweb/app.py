import lux
from lux.utils import test


class TestLuxWeb(test.TestCase):
    config = 'luxweb.config'

    def test_app(self):
        app = self.application()
        self.assertTrue(app)

    def testHome(self):
        http = self.client()
        response = http.get('/')
        self.assertTrue(response.status_code, 200)
        self.assertTrue(response.headers['content-type'], 'text/html')
