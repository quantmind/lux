from lux.utils import test
from lux.extensions.rest import RestField


class TestUtils(test.TestCase):

    def test_rest_column(self):
        col = RestField('bla')
        info = col.tojson()
        self.assertEqual(info['name'], 'bla')
        self.assertEqual(info['field'], 'bla')
