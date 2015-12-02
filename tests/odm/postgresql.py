from dateutil.parser import parse

from lux.utils import test


class TestPostgreSqlBase(test.AppTestCase):
    config_file = 'tests.odm'
    config_params = {
        'DATASTORE': 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'}
    su_credentials = {'username': 'pippo',
                      'password': 'pluto'}

    @classmethod
    def populatedb(cls):
        backend = cls.app.auth_backend
        backend.create_superuser(cls.app.wsgi_request(),
                                 email='pippo@pippo.com',
                                 first_name='Pippo',
                                 **cls.su_credentials)

    def _token(self, credentials=None):
        '''Create an authentication token
        '''
        if credentials is None:
            credentials = self.su_credentials
        request = yield from self.client.post('/authorizations',
                                              content_type='application/json',
                                              body=credentials)
        response = request.response
        self.assertEqual(response.status_code, 201)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())
        data = self.json(response)
        self.assertTrue('token' in data)
        return data['token']

    def _create_task(self, token, subject='This is a task', person=None,
                     **data):
        data['subject'] = subject
        if person:
            data['assigned'] = person['id']
        request = yield from self.client.post(
            '/tasks', body=data, token=token,
            content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 201)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        self.assertEqual(data['subject'], subject)
        self.assertTrue('created' in data)
        return data

    def _get_task(self, token, id):
        request = yield from self.client.get(
            '/tasks/{}'.format(id),
            token=token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        return data

    def _delete_task(self, token, id):
        request = yield from self.client.delete(
            '/tasks/{}'.format(id),
            token=token)
        response = request.response
        self.assertEqual(response.status_code, 204)

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

    def _update_person(self, token, id, username=None, name=None):
        request = yield from self.client.post(
            '/people/{}'.format(id),
            body={'username': username, 'name': name},
            token=token,
            content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        if name:
            self.assertEqual(data['name'], name)
        return data


class TestPostgreSql(TestPostgreSqlBase):

    def test_odm(self):
        tables = yield from self.app.odm.tables()
        self.assertTrue(tables)
        self.assertEqual(len(tables), 1)
        self.assertEqual(len(tables[0][1]), 10)

    def test_rest_model(self):
        from tests.odm import CRUDTask, CRUDPerson
        model = CRUDTask().model(self.app)
        self.assertEqual(model.name, 'task')
        columns = model.columns(self.app)
        self.assertTrue(columns)

        model = CRUDPerson().model(self.app)
        self.assertEqual(model, CRUDPerson().model(self.app))

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

    def test_get_tasks_multi(self):
        url = '/tasks?id=1&id=2&id=3'
        request = yield from self.client.get(url)
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
        self.assertEqual(len(columns), 6)

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

    def test_sortby(self):
        token = yield from self._token()
        yield from self._create_task(token, 'We want to sort 1')
        yield from self._create_task(token, 'We want to sort 2')
        request = yield from self.client.get('/tasks?sortby=created')
        data = self.json(request.response, 200)
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

    def test_sortby_non_existent(self):
        token = yield from self._token()
        yield from self._create_task(token, 'a task')
        yield from self._create_task(token, 'another task')
        request = yield from self.client.get('/tasks?sortby=fgjsdgj')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)

    def test_relationship_field(self):
        token = yield from self._token()
        person = yield from self._create_person(token, 'spiderman')
        task = yield from self._create_task(token, 'climb a wall a day',
                                            person)
        self.assertTrue('assigned' in task)

    def test_relationship_field_failed(self):
        token = yield from self._token()
        data = {'subject': 'climb a wall a day',
                'assigned': 6868897}
        request = yield from self.client.post('/tasks', body=data,
                                              token=token,
                                              content_type='application/json')
        self.assertValidationError(request.response, 'assigned',
                                   'Invalid person')

    def test_unique_field(self):
        token = yield from self._token()
        yield from self._create_person(token, 'spiderman1', 'luca')
        data = dict(username='spiderman1', name='john')
        request = yield from self.client.post('/people', body=data,
                                              token=token,
                                              content_type='application/json')
        self.assertValidationError(request.response, 'username',
                                   'spiderman1 not available')

    def test_unique_field_update_fail(self):
        """
        Tests that it's not possible to update a unique field of an
        existing record to that of another
        """
        token = yield from self._token()
        yield from self._create_person(token, 'spiderfail1', 'luca')
        data = yield from self._create_person(token, 'spiderfail2', 'luca')

        request = yield from self.client.post(
            '/people/{}'.format(data['id']),
            body={'username': 'spiderfail1', 'name': 'luca'},
            token=token,
            content_type='application/json')
        response = request.response
        self.assertValidationError(response, 'username',
                                   'spiderfail1 not available')

    def test_unique_field_update_unchanged(self):
        """
        Tests that an update of an existing model instance works if the the
        unique field hasn't changed
        """
        token = yield from self._token()
        data = yield from self._create_person(token, 'spiderstale1', 'luca')
        yield from self._update_person(token, data['id'], 'spiderstale1',
                                       'lucachanged')

    def test_enum_field(self):
        token = yield from self._token()
        data = yield from self._create_task(token, enum_field='opt1')
        self.assertEqual(data['enum_field'], 'opt1')
        data = yield from self._get_task(token, id=data['id'])
        self.assertEqual(data['enum_field'], 'opt1')

    def test_enum_field_fail(self):
        token = yield from self._token()
        request = yield from self.client.post(
            '/tasks',
            body={'enum_field': 'opt3'},
            token=token,
            content_type='application/json')
        response = request.response
        self.assertValidationError(response, 'enum_field',
                                   'opt3 is not a valid choice')

    def test_metadata_custom(self):
        request = yield from self.client.get('/users/metadata',
                                             content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        columns = data['columns']
        self.assertEqual(len(columns), 8)

    def test_preflight_request(self):
        request = yield from self.client.options('/users')
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Methods'],
                         'GET, POST, DELETE')
        token = yield from self._token()
        task = yield from self._create_task(token, 'testing preflight on id')
        request = yield from self.client.options('/tasks/%s' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Methods'],
                         'GET, POST, DELETE')

    def test_head_request(self):
        request = yield from self.client.head('/tasks/8676097')
        response = request.response
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.content)
        token = yield from self._token()
        task = yield from self._create_task(token, 'testing head request')
        request = yield from self.client.head('/tasks/%s' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.content)

    def test_filter(self):
        token = yield from self._token()
        yield from self._create_task(token, 'A done task', done=True)
        yield from self._create_task(token, 'a not done task')
        request = yield from self.client.get('/tasks?done=1')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(result)
        for task in result:
            self.assertEqual(task['done'], True)

        request = yield from self.client.get('/tasks?done=0')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(result)
        for task in result:
            self.assertEqual(task['done'], False)

    def test_multi_relationship_field(self):
        from lux.extensions.odm import RelationshipField, RestModel
        field = RelationshipField(RestModel('book'), name='test_book',
                                  multiple=True)
        self.assertEqual(field._model.name, 'book')
        attrs = field.getattrs()
        self.assertEqual(attrs.get('multiple'), True)
        self.assertEqual(attrs.get('label'), 'Test book')

    def test_limit(self):
        token = yield from self._token()
        yield from self._create_task(token, 'whatever')
        yield from self._create_task(token, 'do everything')
        request = yield from self.client.get('/tasks?limit=-1')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 2)
        request = yield from self.client.get('/tasks?limit=-1&offset=-89')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 2)
        request = yield from self.client.get('/tasks?limit=sdc&offset=hhh')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 2)
