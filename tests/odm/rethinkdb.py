from lux.utils import test

from tests.odm import Author


class TestSql(test.AppTestCase):
    config_file = 'tests.odm'
    config_params = {'DATASTORE': 'rethinkdb://127.0.0.1:28015/luxtests'}

    def test_odm(self):
        odm = self.app.odm
        self.assertEqual(len(odm), 2)
        sql = odm('nosql')
        tables = sql.tables()
        self.assertTrue(tables)

    def test_simple_session(self):
        app = self.app
        odm = app.odm('nosql')
        with odm.begin() as s:
            self.assertEqual(s.app, app)
            user = odm.user(name='Luca')
            s.add(user)

        self.assertTrue(user.id)
