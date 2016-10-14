from unittest.mock import MagicMock

from lux.utils import test

from tests.odm.utils import SqliteMixin, OdmUtils


class TestFiltersPsql(OdmUtils, test.AppTestCase):

    async def test_filter(self):
        token = await self._token('testuser')
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

    async def test_notequals(self):
        request = await self.client.get('/tasks?desc:ne=abu')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['desc'], 'genie')

        request = await self.client.get('/tasks?desc:ne=')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertEqual(len(result), 2)

        request = await self.client.get(
            '/tasks?desc:ne=abu&desc:ne=genie')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertEqual(len(result), 0)

        # multiple values with one empty value should not do odd things
        request = await self.client.get(
            '/tasks?desc:ne=abu&desc:ne=')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['desc'], 'genie')

    async def test_search(self):
        request = await self.client.get('/tasks?subject:search=rescue to the')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        request = await self.client.get('/tasks?subject:search=pippo')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) == 1)
        self.assertTrue('pippo' in result[0]['subject'])

        request = await self.client.get('/tasks?subject:search=thebe')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

        # if multiple values are provided, only the first one should be used
        request = await self.client.get(
            '/tasks?subject:search=pippo&subject:search=thebe')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) == 1)
        self.assertTrue('pippo' in result[0]['subject'])

    async def test_load_only(self):
        request = await self.client.get(
            '/tasks?load_only=id&load_only=subject')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        for entry in result:
            self.assertEqual(len(entry), 2)
            self.assertTrue(entry['id'])
            self.assertTrue(entry['subject'])

    async def test_load_only_1(self):
        request = await self.client.get(
            '/tasks?load_only=id&load_only=id')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        for entry in result:
            self.assertEqual(len(entry), 1)
            self.assertTrue(entry['id'])

    async def test_load_only_with_url(self):
        request = await self.client.get(
            '/tasks?load_only=api_url&load_only=subject')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        for entry in result:
            self.assertEqual(len(entry), 2)
            self.assertTrue(entry['api_url'])
            self.assertTrue(entry['subject'])

    @test.green
    def test_error_multiple(self):
        request = self.app.wsgi_request()
        logger = MagicMock()
        request.cache.logger = logger
        instance = self.app.models['tasks'].get_instance(request, done=False)
        self.assertTrue(instance)
        self.assertEqual(logger.error.called, 1)


class TestFiltersSqlite(SqliteMixin, TestFiltersPsql):

    def test_search(self):
        # MATCH is not implemented in SQLite
        pass
