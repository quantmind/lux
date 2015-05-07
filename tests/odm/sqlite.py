import json

from pulsar.apps.test import test_timeout

from lux.utils import test


class TestSql(test.AppTestCase):
    config_file = 'tests.odm'
    config_params = {'DATASTORE': 'sqlite://'}

    def test_odm(self):
        odm = self.app.odm()
        tables = odm.tables()
        self.assertTrue(tables)

    def test_simple_session(self):
        app = self.app
        odm = app.odm()
        with odm.begin() as session:
            self.assertEqual(session.app, app)
            user = odm.user(first_name='Luca')
            session.add(user)

        self.assertTrue(user.id)
        self.assertEqual(user.first_name, 'Luca')
        self.assertFalse(user.is_superuser())

    def test_get_tasks(self):
        request = self.client.get('/tasks')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, list)

    def test_create_task(self):
        data = {'subject': 'This is my first task'}
        request = self.client.post('/tasks', body=data,
                                   content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 201)
