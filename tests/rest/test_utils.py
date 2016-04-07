from lux.utils import test
from lux.extensions.rest import RestColumn


class TestUtils(test.TestCase):

    def test_rest_column(self):
        col = RestColumn('bla')
        info = col.as_dict()
        self.assertEqual(info['name'], 'bla')
        self.assertEqual(info['field'], 'bla')
