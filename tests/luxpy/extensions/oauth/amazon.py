from lux.utils import test
from lux.extensions.services import api


@test.skipUnless(test.get_params('AMAZON_CLIENT_ID',
                                 'AMAZON_CLIENT_SECRET'),
                 'amazon_id & amazon_secret parameters required in'
                 ' test_settings.py file.')
class TestAmazon(test.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = api('amazon', cfg)
        r = g.authorization(note=cls.note)
        cls.auth_result = r
        cls.g = g
