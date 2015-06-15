import json

from dateutil.parser import parse

from lux.utils import test


@test.test_timeout(20)
class TestCMSsqlite(test.AppTestCase):
    config_file = 'tests.cms'
    config_params = {'DATASTORE': 'sqlite://'}

    def _create_page(self, path='', title='a page', template=None,
                     layout=None):
        if template is None:
            data = dict(body='$html_main', title='simple')
            request = yield from self.client.post(
                '/api/html_templates',
                body=data,
                content_type='application/json')
            response = request.response
            self.assertEqual(response.status_code, 201)
            data = self.json(response)
            template = data['id']
        if not layout:
            layout = json.dumps({})
        data = dict(path=path, title=title, template_id=template,
                    layout=layout)
        request = yield from self.client.post(
            '/api/html_pages', body=data, content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 201)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        self.assertEqual(data['title'], title)
        return data

    def test_odm(self):
        tables = yield from self.app.odm.tables()
        self.assertTrue(tables)

    def test_get_pages(self):
        request = yield from self.client.get('/api/html_pages')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        result = data['result']
        self.assertIsInstance(result, list)

    def test_metadata(self):
        request = yield from self.client.get('/api/html_pages/metadata')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['columns'], list)

    def test_create_page(self):
        return self._create_page()


class d:

    def test_update_task(self):
        task = yield from self._create_task('This is another task')
        # Update task
        request = yield from self.client.post(
            '/tasks/%d' % task['id'],
            body={'done': True},
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
        task = yield from self._create_task('A task to be deleted')
        # Delete task
        request = yield from self.client.delete('/tasks/%d' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 204)
        #
        request = yield from self.client.get('/tasks/%d' % task['id'])
        response = request.response
        self.assertEqual(response.status_code, 404)

    def test_get_sortby(self):
        yield from self._create_task('We want to sort 1')
        yield from self._create_task('We want to sort 2')
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
        person = yield from self._create_person('spiderman')
        task = yield from self._create_task('climb a wall a day', person)
        self.assertTrue('assigned' in task)

    def test_relationship_field_failed(self):
        data = {'subject': 'climb a wall a day',
                'assigned': 6868897}
        request = yield from self.client.post('/tasks', body=data,
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
        person = yield from self._create_person('spiderman1', 'luca')
        data = dict(username='spiderman1', name='john')
        request = yield from self.client.post('/people', body=data,
                                              content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertFalse(data['success'])
        self.assertTrue(data['error'])
        error = data['messages']['username'][0]
        self.assertEqual(error['message'], 'spiderman1 not available')
