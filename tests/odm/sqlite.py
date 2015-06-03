import json

from pulsar.apps.test import test_timeout

from dateutil.parser import parse

from lux.utils import test


class TestSql(test.AppTestCase):
    config_file = 'tests.odm'
    config_params = {'DATASTORE': 'sqlite://'}

    def _create_task(self, txt='This is a task', person=None):
        data = {'subject': txt}
        if person:
            data['assigned'] = person['id']
        request = self.client.post('/tasks', body=data,
                                   content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 201)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        self.assertEqual(data['subject'], txt)
        self.assertTrue('created' in data)
        self.assertFalse(data['done'])
        return data

    def _create_person(self, username, name=None):
        name = name or username
        request = self.client.post('/people',
                                   body={'username': username,
                                         'name': name},
                                   content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 201)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        self.assertEqual(data['name'], name)
        return data

    def test_odm(self):
        odm = self.app.odm()
        tables = odm.tables()
        self.assertTrue(tables)

    def test_rest_model(self):
        from tests.odm import CRUDTask, CRUDPerson
        model = CRUDTask.model
        self.assertEqual(model.name, 'task')
        columns = model.columns(self.app)
        self.assertTrue(columns)

        model = CRUDPerson.model
        self.assertEqual(model.name, 'person')
        self.assertEqual(model.url, 'people')
        self.assertEqual(model.api_name, 'people_url')
        columns = model.columns(self.app)
        self.assertTrue(columns)

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
        self.assertIsInstance(data, dict)
        result = data['result']
        self.assertIsInstance(result, list)

    def test_metadata(self):
        request = self.client.get('/tasks/metadata')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['columns'], list)

    def test_create_task(self):
        self._create_task()

    def test_update_task(self):
        task = self._create_task('This is another task')
        # Update task
        request = self.client.post('/tasks/%d' % task['id'],
                                   body={'done': True},
                                   content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertEqual(data['id'], task['id'])
        self.assertEqual(data['done'], True)
        #
        request = self.client.get('/tasks/%d' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], task['id'])
        self.assertEqual(data['done'], True)

    def test_delete_task(self):
        task = self._create_task('A task to be deleted')
        # Delete task
        request = self.client.delete('/tasks/%d' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 204)
        #
        request = self.client.get('/tasks/%d' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 404)

    def test_get_sortby(self):
        self._create_task('We want to sort 1')
        self._create_task('We want to sort 2')
        request = self.client.get('/tasks?sortby=created')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        result = data['result']
        self.assertIsInstance(result, list)
        for task1, task2 in zip(result, result[1:]):
            dt1 = parse(task1['created'])
            dt2 = parse(task2['created'])
            self.assertTrue(dt2 > dt1)
        #
        request = self.client.get('/tasks?sortby=created:desc')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        result = data['result']
        self.assertIsInstance(result, list)
        for task1, task2 in zip(result, result[1:]):
            dt1 = parse(task1['created'])
            dt2 = parse(task2['created'])
            self.assertTrue(dt2 < dt1)

    def test_relationship_field(self):
        person = self._create_person('spiderman')
        task = self._create_task('climb a wall a day', person)
        self.assertTrue('assigned' in task)

    def test_relationship_field_failed(self):
        data = {'subject': 'climb a wall a day',
                'assigned': 6868897}
        request = self.client.post('/tasks', body=data,
                                   content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertFalse(data['success'])
        self.assertTrue(data['error'])
        error = data['messages']['assigned'][0]
        self.assertEqual(error['message'], 'Invalid person')

    def test_unique_field(self):
        person = self._create_person('spiderman1', 'luca')
        data = dict(username='spiderman1', name='john')
        request = self.client.post('/people', body=data,
                                   content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertFalse(data['success'])
        self.assertTrue(data['error'])
        error = data['messages']['username'][0]
        self.assertEqual(error['message'], 'spiderman1 not available')
