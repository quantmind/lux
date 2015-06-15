from dateutil.parser import parse

from pulsar.apps.test import test_timeout

from lux.utils import test


@test_timeout(20)
class TestSql(test.AppTestCase):
    config_file = 'tests.odm'
    config_params = {'DATASTORE': 'sqlite://'}
    credentials = {'username': 'pippo',
                   'password': 'pluto'}

    @classmethod
    def populatedb(cls):
        backend = cls.app.auth_backend
        backend.create_superuser(cls.app.wsgi_request(),
                                 email='pippo@pippo.com',
                                 first_name='Pippo',
                                 **cls.credentials)

    def _token(self):
        '''Create an authentication token
        '''
        request = yield from self.client.post('/authorizations',
                                              content_type='application/json',
                                              body=self.credentials)
        response = request.response
        self.assertEqual(response.status_code, 201)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())
        data = self.json(response)
        self.assertTrue('token' in data)
        return data['token']

    def _create_task(self, token, txt='This is a task', person=None):
        data = {'subject': txt}
        if person:
            data['assigned_id'] = person['id']
        request = yield from self.client.post(
            '/tasks', body=data, token=token,
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

    def _create_person(self, token, username, name=None):
        name = name or username
        request = yield from self.client.post(
            '/people',
            body={'username': username, 'name': name},
            token=token,
            content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 201)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        self.assertEqual(data['name'], name)
        return data

    def test_odm(self):
        tables = yield from self.app.odm.tables()
        self.assertTrue(tables)
        self.assertEqual(len(tables), 1)
        self.assertEqual(len(tables[0][1]), 8)

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

    @test.green
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
        request = yield from self.client.get('/tasks')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        result = data['result']
        self.assertIsInstance(result, list)

    def test_metadata(self):
        request = yield from self.client.get('/tasks/metadata')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        columns = data['columns']
        self.assertIsInstance(columns, list)
        self.assertEqual(len(columns), 5)

    def test_create_task(self):
        token = yield from self._token()
        yield from self._create_task(token)

    def test_update_task(self):
        token = yield from self._token()
        task = yield from self._create_task(token, 'This is another task')
        # Update task
        request = yield from self.client.post(
            '/tasks/%d' % task['id'],
            body={'done': True},
            content_type='application/json')

        response = request.response
        self.assertEqual(response.status_code, 403)
        #
        # Update task
        request = yield from self.client.post(
            '/tasks/%d' % task['id'],
            body={'done': True}, token=token,
            content_type='application/json')

        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertEqual(data['id'], task['id'])
        self.assertEqual(data['done'], True)
        #
        request = yield from self.client.get('/tasks/%d' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], task['id'])
        self.assertEqual(data['done'], True)

    def test_delete_task(self):
        token = yield from self._token()
        task = yield from self._create_task(token, 'A task to be deleted')
        # Delete task
        request = yield from self.client.delete('/tasks/%d' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 403)
        # Delete task
        request = yield from self.client.delete('/tasks/%d' % task['id'],
                                                token=token)
        response = request.response
        self.assertEqual(response.status_code, 204)
        #
        request = yield from self.client.get('/tasks/%d' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 404)

    def test_get_sortby(self):
        token = yield from self._token()
        yield from self._create_task(token, 'We want to sort 1')
        yield from self._create_task(token, 'We want to sort 2')
        request = yield from self.client.get('/tasks?sortby=created')
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
        request = yield from self.client.get('/tasks?sortby=created:desc')
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
        token = yield from self._token()
        person = yield from self._create_person(token, 'spiderman')
        task = yield from self._create_task(token, 'climb a wall a day',
                                            person)
        self.assertTrue('assigned_id' in task)

    def test_relationship_field_failed(self):
        token = yield from self._token()
        data = {'subject': 'climb a wall a day',
                'assigned_id': 6868897}
        request = yield from self.client.post('/tasks', body=data,
                                              token=token,
                                              content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertFalse(data['success'])
        self.assertTrue(data['error'])
        error = data['messages']['assigned_id'][0]
        self.assertEqual(error['message'], 'Invalid person')

    def test_unique_field(self):
        token = yield from self._token()
        yield from self._create_person(token, 'spiderman1', 'luca')
        data = dict(username='spiderman1', name='john')
        request = yield from self.client.post('/people', body=data,
                                              token=token,
                                              content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertFalse(data['success'])
        self.assertTrue(data['error'])
        error = data['messages']['username'][0]
        self.assertEqual(error['message'], 'spiderman1 not available')

    def test_metadata_custom(self):
        request = yield from self.client.get('/users/metadata',
                                              content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        columns = data['columns']
        self.assertEqual(len(columns), 8)

    def test_preflight_request(self):
        request = yield from self.client.options('/users/delete')
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Methods'],
                         'GET, POST, DELETE')
