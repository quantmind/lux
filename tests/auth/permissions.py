from tests.auth.utils import deadline


class PermissionsMixin:

    async def test_create_permission_errors(self):
        """Test permissions CREATE/UPDATE/DELETE"""
        token = await self._token('testuser')
        request = await self.client.post('/permissions',
                                         json=dict(name='blabla'),
                                         token=token)
        self.assertValidationError(request.response, 'policy', 'required')
        #
        data = dict(name='blabla', policy='{')
        request = await self.client.post('/permissions',
                                         json=data,
                                         token=token)
        self.assertValidationError(request.response, 'policy',
                                   'not a valid JSON string')
        #
        data = dict(name='blabla', description='hgv hh', policy='[]')
        request = await self.client.post('/permissions',
                                         json=data,
                                         token=token)
        self.assertValidationError(request.response, '',
                                   text='Policy empty')
        #
        data = dict(name='blabla', description='hgv hh', policy='67')
        request = await self.client.post('/permissions',
                                         json=data,
                                         token=token)
        self.assertValidationError(request.response, '',
                                   text='Policy should be a list or an object')
        #
        data = dict(name='blabla', description='hgv hh', policy='[45]')
        request = await self.client.post('/permissions',
                                         json=data,
                                         token=token)
        self.assertValidationError(request.response, '',
                                   text='Policy should be a list or an object')
        #
        data = dict(name='blabla', description='hgv hh', policy='{}')
        request = await self.client.post('/permissions',
                                         json=data,
                                         token=token)
        self.assertValidationError(request.response, '',
                                   text='"resource" must be defined')

    async def test_column_permissions_read(self):
        """Tests read requests against columns with permission level 0"""
        su_token = await self._token('testuser')

        objective = await self._create_objective(su_token)

        request = await self.client.get(
            '/objectives/{}'.format(objective['id']))
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertFalse('deadline' in data)

        request = await self.client.get('/objectives')
        data = self.json(request.response, 200)
        self.assertTrue('result' in data)
        for item in data['result']:
            self.assertTrue('id' in item)
            self.assertFalse('deadline' in item)

        request = await self.client.get('/objectives/metadata')
        data = self.json(request.response, 200)
        self.assertFalse(
            any(field['name'] == 'deadline' for field in data['columns']))

        request = await self.client.get(
            '/objectives/{}'.format(objective['id']), token=su_token)
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('deadline' in data)

        request = await self.client.get(
            '/objectives', token=su_token)
        data = self.json(request.response, 200)
        self.assertTrue('result' in data)
        for item in data['result']:
            self.assertTrue('id' in item)
            if item['id'] == objective['id']:
                self.assertTrue('deadline' in item)

        request = await self.client.get(
            '/objectives/metadata', token=su_token)
        data = self.json(request.response, 200)
        self.assertTrue(
            any(field['name'] == 'deadline' for field in data['columns']))

    async def test_column_permissions_update_create(self):
        """
        Tests create and update requests against columns
        with permission levels 10 and 20
        """
        su_token = await self._token('testuser')

        objective = await self._create_objective(su_token,
                                                 outcome="under achieved")
        self.assertTrue('deadline' in objective)
        self.assertTrue('outcome' in objective)

        request = await self.client.post(
            '/objectives/{}'.format(objective['id']),
            json={
                'deadline': deadline(20),
                'outcome': 'exceeded'
            })
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('outcome' in data)
        self.assertEqual(data['outcome'], "exceeded")
        self.assertFalse('deadline' in data)

        request = await self.client.get(
            '/objectives/{}'.format(objective['id']), token=su_token)
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('subject' in data)
        self.assertTrue('outcome' in data)
        self.assertTrue('deadline' in data)
        self.assertEqual(data['deadline'], deadline(10))
        self.assertEqual(data['outcome'], "exceeded")

    async def test_column_permissions_policy(self):
        """
        Checks that a custom policy works on a column with default access
        level 0
        """
        user_token = await self._token('pippo')
        objective = await self._create_objective(user_token)

        request = await self.client.get(
            '/objectives/{}'.format(objective['id']), token=user_token)
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('subject' in data)

        request = await self.client.get(
            '/objectives', token=user_token)
        data = self.json(request.response, 200)
        self.assertTrue('result' in data)
        for item in data['result']:
            self.assertTrue('id' in item)
            self.assertTrue('subject' in item)

        request = await self.client.get(
            '/objectives/metadata', token=user_token)
        data = self.json(request.response, 200)
        self.assertTrue(
            any(field['name'] == 'deadline' for field in data['columns']))

        request = await self.client.post(
            '/objectives/{}'.format(objective['id']),
            token=user_token,
            json={'subject': 'subject changed',
                  'deadline': deadline(20)}
        )

        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('deadline' in data)
        self.assertEqual(data['deadline'], deadline(20))
        self.assertEqual(data['subject'], "subject changed")
