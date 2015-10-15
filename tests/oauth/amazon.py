from lux.utils import test


@test.skipUnless(test.get_params('AMAZON_CLIENT_ID',
                                 'AMAZON_CLIENT_SECRET'),
                 'amazon_id & amazon_secret parameters required in'
                 ' test_settings.py file.')
class TestAmazon(test.TestCase):
    pass
