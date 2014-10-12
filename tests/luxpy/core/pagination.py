__test__ = False
import lux
from lux.utils import test
from lux.extensions import api


class TestTable(test.TestCase):

    def testColumn(self):
        c = lux.column('bla-foo')
        self.assertEqual(c.code, 'bla-foo')
        self.assertEqual(c.name, 'Bla foo')
        self.assertEqual(c.description, None)
        self.assertEqual(c.attrname, 'bla_foo')
        self.assertEqual(c.fields, ('bla_foo',))

    def test_table_html(self):
        table = lux.Table(('id', 'name', 'email'))
        User = api.create_model('User', 'id', 'name', 'email')
        self.assertEqual(template.columns[0].code, 'id')
        self.assertEqual(template.columns[1].code, 'name')
        self.assertEqual(template.columns[1].code, 'email')
        users = User.create_many([(1, 'bla', 'bla@foo.com'),
                                  (2, 'pippo', 'pippo@foo.com'),
                                  (3, 'pluto', 'pluto@foo.com'),
                                  (4, 'luna', 'luna@foo.com')])
        model = lux.create_model('bla', 'foo')
        data = lux.DataTable([[1, 3], ['bla', 'foo']])
        html = table(None, data, ('text/html',))
        self.assertEqual(html.tag, 'table')
