from .postgresql import TestPostgreSqlBase
from .sqlite import TestSqliteMixin


class TestFiltersPsql(TestPostgreSqlBase):
    @classmethod
    def populatedb(cls):
        super(TestPostgreSqlBase, cls).populatedb()
        odm = cls.app.odm()

        with odm.begin() as session:
            cls.pippo = odm.task(
                subject='pippo to the rescue',
                desc='abu'
            )
            cls.pluto = odm.task(
                subject='pluto to the rescue',
                desc='genie'
            )
            cls.earth = odm.task(
                subject='earth is the centre of the universe',
                desc=None
            )
            session.add(cls.pippo)
            session.add(cls.pluto)
            session.add(cls.earth)

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


class TestFiltersSqlite(TestSqliteMixin, TestFiltersPsql):
    def test_search(self):
        # MATCH is not implemented in SQLite
        pass
