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

    async def _token(self, credentials=None):
        '''Create an authentication token
        '''
        if credentials is None:
            credentials = self.su_credentials
        request = await self.client.post('/authorizations',
                                         content_type='application/json',
                                         body=credentials)
        response = request.response
        self.assertEqual(response.status_code, 201)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())
        data = self.json(response)
        self.assertTrue('token' in data)
        return data['token']

    async def _create_task(self, token, subject='This is a task', person=None,
                           **data):
        data['subject'] = subject
        if person:
            data['assigned'] = person['id']
        request = await self.client.post(
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

    async def _get_task(self, token, id):
        request = await self.client.get(
            '/tasks/{}'.format(id),
            token=token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        return data

    async def _delete_task(self, token, id):
        request = await self.client.delete(
            '/tasks/{}'.format(id),
            token=token)
        response = request.response
        self.assertEqual(response.status_code, 204)

    async def _create_person(self, token, username, name=None):
        name = name or username
        request = await self.client.post(
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

    async def _update_person(self, token, id, username=None, name=None):
        request = await self.client.post(
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

    async def test_odm(self):
        tables = await self.app.odm.tables()
        self.assertTrue(tables)
        self.assertEqual(len(tables), 1)
        self.assertEqual(len(tables[0][1]), 10)

    def test_rest_model(self):
        from tests.odm import CRUDTask, CRUDPerson
        model = self.app.models.register(CRUDTask().model)
        self.assertEqual(model.name, 'task')
        columns = model.columns()
        self.assertTrue(columns)

        model = self.app.models.register(CRUDPerson().model)
        self.assertEqual(model,
                         self.app.models.register(CRUDPerson().model))

        self.assertEqual(model.name, 'person')
        self.assertEqual(model.url, 'people')
        self.assertEqual(model.api_name, 'people_url')
        columns = model.columns()
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

    async def test_get_tasks(self):
        request = await self.client.get('/tasks')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        result = data['result']
        self.assertIsInstance(result, list)

    async def test_get_tasks_multi(self):
        url = '/tasks?id=1&id=2&id=3'
        request = await self.client.get(url)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        result = data['result']
        self.assertIsInstance(result, list)

    async def test_metadata(self):
        request = await self.client.get('/tasks/metadata')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        columns = data['columns']
        self.assertIsInstance(columns, list)
        self.assertEqual(len(columns), 7)

    async def test_create_task(self):
        token = await self._token()
        await self._create_task(token)

    async def test_update_task(self):
        token = await self._token()
        task = await self._create_task(token, 'This is another task')
        # Update task
        request = await self.client.post(
            '/tasks/%d' % task['id'],
            body={'done': True},
            content_type='application/json')

        response = request.response
        self.assertEqual(response.status_code, 403)
        #
        # Update task
        request = await self.client.post(
            '/tasks/%d' % task['id'],
            body={'done': True}, token=token,
            content_type='application/json')

        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertEqual(data['id'], task['id'])
        self.assertEqual(data['done'], True)
        #
        request = await self.client.get('/tasks/%d' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], task['id'])
        self.assertEqual(data['done'], True)

    async def test_delete_task(self):
        token = await self._token()
        task = await self._create_task(token, 'A task to be deleted')
        # Delete task
        request = await self.client.delete('/tasks/%d' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 403)
        # Delete task
        request = await self.client.delete('/tasks/%d' % task['id'],
                                           token=token)
        response = request.response
        self.assertEqual(response.status_code, 204)
        #
        request = await self.client.get('/tasks/%d' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 404)

    async def test_sortby(self):
        token = await self._token()
        await self._create_task(token, 'We want to sort 1')
        await self._create_task(token, 'We want to sort 2')
        request = await self.client.get('/tasks?sortby=created')
        data = self.json(request.response, 200)
        self.assertIsInstance(data, dict)
        result = data['result']
        self.assertIsInstance(result, list)
        for task1, task2 in zip(result, result[1:]):
            dt1 = parse(task1['created'])
            dt2 = parse(task2['created'])
            self.assertTrue(dt2 > dt1)
        #
        request = await self.client.get('/tasks?sortby=created:desc')
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

    async def test_sortby_non_existent(self):
        token = await self._token()
        await self._create_task(token, 'a task')
        await self._create_task(token, 'another task')
        request = await self.client.get('/tasks?sortby=fgjsdgj')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)

    async def test_relationship_field(self):
        token = await self._token()
        person = await self._create_person(token, 'spiderman')
        task = await self._create_task(token, 'climb a wall a day',
                                       person)
        self.assertTrue('assigned' in task)

    async def test_relationship_field_failed(self):
        token = await self._token()
        data = {'subject': 'climb a wall a day',
                'assigned': 6868897}
        request = await self.client.post('/tasks', body=data,
                                         token=token,
                                         content_type='application/json')
        self.assertValidationError(request.response, 'assigned',
                                   'Invalid person')

    async def test_unique_field(self):
        token = await self._token()
        await self._create_person(token, 'spiderman1', 'luca')
        data = dict(username='spiderman1', name='john')
        request = await self.client.post('/people', body=data,
                                         token=token,
                                         content_type='application/json')
        self.assertValidationError(request.response, 'username',
                                   'spiderman1 not available')

    async def test_unique_field_update_fail(self):
        """
        Tests that it's not possible to update a unique field of an
        existing record to that of another
        """
        token = await self._token()
        await self._create_person(token, 'spiderfail1', 'luca')
        data = await self._create_person(token, 'spiderfail2', 'luca')

        request = await self.client.post(
            '/people/{}'.format(data['id']),
            body={'username': 'spiderfail1', 'name': 'luca'},
            token=token,
            content_type='application/json')
        response = request.response
        self.assertValidationError(response, 'username',
                                   'spiderfail1 not available')

    async def test_unique_field_update_unchanged(self):
        """
        Tests that an update of an existing model instance works if the the
        unique field hasn't changed
        """
        token = await self._token()
        data = await self._create_person(token, 'spiderstale1', 'luca')
        await self._update_person(token, data['id'], 'spiderstale1',
                                  'lucachanged')

    async def test_enum_field(self):
        token = await self._token()
        data = await self._create_task(token, enum_field='opt1')
        self.assertEqual(data['enum_field'], 'opt1')
        data = await self._get_task(token, id=data['id'])
        self.assertEqual(data['enum_field'], 'opt1')

    async def test_enum_field_fail(self):
        token = await self._token()
        request = await self.client.post(
            '/tasks',
            body={'enum_field': 'opt3'},
            token=token,
            content_type='application/json')
        response = request.response
        self.assertValidationError(response, 'enum_field',
                                   'opt3 is not a valid choice')

    async def test_metadata_custom(self):
        request = await self.client.get('/users/metadata',
                                        content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        columns = data['columns']
        self.assertEqual(len(columns), 9)

    async def test_preflight_request(self):
        request = await self.client.options('/users')
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Methods'],
                         'GET, POST, DELETE')
        token = await self._token()
        task = await self._create_task(token, 'testing preflight on id')
        request = await self.client.options('/tasks/%s' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Methods'],
                         'GET, POST, DELETE')

    async def test_head_request(self):
        request = await self.client.head('/tasks/8676097')
        response = request.response
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.content)
        token = await self._token()
        task = await self._create_task(token, 'testing head request')
        request = await self.client.head('/tasks/%s' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.content)

    async def test_filter(self):
        token = await self._token()
        await self._create_task(token, 'A done task', done=True)
        await self._create_task(token, 'a not done task')
        request = await self.client.get('/tasks?done=1')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(result)
        for task in result:
            self.assertEqual(task['done'], True)

        request = await self.client.get('/tasks?done=0')
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
        self.assertEqual(field.model.name, 'book')
        attrs = field.getattrs()
        self.assertEqual(attrs.get('multiple'), True)
        self.assertEqual(attrs.get('label'), 'Test book')

    async def test_limit(self):
        token = await self._token()
        await self._create_task(token, 'whatever')
        await self._create_task(token, 'do everything')
        request = await self.client.get('/tasks?limit=-1')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 2)
        request = await self.client.get('/tasks?limit=-1&offset=-89')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 2)
        request = await self.client.get('/tasks?limit=sdc&offset=hhh')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 2)
