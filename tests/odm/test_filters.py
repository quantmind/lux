from lux.utils import test

from tests.odm.utils import SqliteMixin, OdmUtils


class TestFiltersPsql(OdmUtils, test.AppTestCase):

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
        self.assertEqual(result[0]['id'], self.pippo.id)

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
        self.assertEqual(result[0]['id'], self.pippo.id)

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


class TestFiltersSqlite(SqliteMixin, TestFiltersPsql):

    def test_search(self):
        # MATCH is not implemented in SQLite
        pass
