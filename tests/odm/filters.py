from lux.utils import test
from .postgresql import TestPostgreSqlBase
from .sqlite import TestSqliteMixin


@test.sequential
class TestFiltersPsql(TestPostgreSqlBase):

    def setUp(self):
        self.token = yield from self._token()
        self.pippo = yield from self._create_task(self.token,
                                                  'pippo to the rescue',
                                                  desc='abu')
        self.pluto = yield from self._create_task(self.token,
                                                  'pluto to the rescue',
                                                  desc='genie')
        self.earth = yield from self._create_task(self.token,
                                                  'earth is the centre of '
                                                  'the universe',
                                                  desc=None)

    def tearDown(self):
        yield from self._delete_task(self.token, self.pippo['id'])
        yield from self._delete_task(self.token, self.pluto['id'])
        yield from self._delete_task(self.token, self.earth['id'])

    def test_notequals(self):
        request = yield from self.client.get('/tasks?desc:ne=abu')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['desc'], 'genie')

        request = yield from self.client.get('/tasks?desc:ne=')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertEqual(len(result), 2)

    def test_search(self):
        request = yield from self.client.get('/tasks?subject:search=rescue to '
                                             'the')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        request = yield from self.client.get('/tasks?subject:search=pippo')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) == 1)
        self.assertEqual(result[0]['id'], self.pippo['id'])

        request = yield from self.client.get('/tasks?subject:search=thebe')
        data = self.json(request.response, 200)
        result = data['result']
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


@test.sequential
class TestFiltersSqlite(TestSqliteMixin, TestFiltersPsql):
    def test_search(self):
        # MATCH is not implemented in SQLite
        pass
