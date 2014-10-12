'''Geonamesb API'''
from lux.utils import test
from lux.extensions.services import api


@test.skipUnless(test.get_params('GEONAMES_USERNAME'),
                 'GEONAMES_USERNAME required in config.py file.')
class TestGeoNames(test.TestCase):
    note = 'testing python social package'

    @classmethod
    def setUpClass(cls):
        cls.g = api('geonames', cls.cfg)

    def setUp(self):
        self.assertTrue(self.g.has_registration(self.cfg))

    def testCountryInfo(self):
        c = self.g.country_info()
        self.assertTrue(isinstance(c, list))
