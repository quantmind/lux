from pulsar.apps.test import test_timeout

from lux.utils import test


class TestSql(test.AppTestCase):
    config_file = 'tests.odm'
    config_params = {'DATASTORE': 'sqlite://'}

    def test_odm(self):
        odm = self.app.odm
        self.assertEqual(len(odm), 2)
        sql = odm('sql')
        tables = sql.tables()
        self.assertTrue(tables)

    def test_simple_session(self):
        app = self.app
        sql = app.odm('sql')
        with sql.begin() as s:
            self.assertEqual(s.app, app)
            author = sql.author(name='Luca')
            s.add(author)

        with sql.begin() as s:
            s.add(author)
            self.assertTrue(author.id)
