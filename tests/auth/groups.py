

class GroupsMixin:

    async def test_group_validation(self):
        token = await self._token('testuser')
        payload = {'name': 'abc'}
        request = await self.client.post('/groups',
                                         json=payload,
                                         token=token)
        data = self.json(request.response, 201)
        gid = data['id']
        payload['name'] = 'abcd'
        request = await self.client.post('/groups/abc',
                                         json=payload,
                                         token=token)

        data = self.json(request.response, 200)
        self.assertEqual(data['name'], 'abcd')
        self.assertEqual(data['id'], gid)

        payload['name'] = 'ABCd'
        request = await self.client.post('/groups',
                                         json=payload,
                                         token=token)

        self.assertValidationError(request.response, 'name',
                                   'Only lower case, alphanumeric characters '
                                   'and hyphens are allowed')

    async def test_add_user_to_group(self):
        credentials = await self._new_credentials()
        username = credentials['username']
        token = await self._token('testuser')
        request = await self.client.put('/users/%s' % username,
                                        json={'groups': ['users']},
                                        token=token)
        data = self.json(request.response, 200)
        self.assertTrue('groups[]' in data)

    async def test_add_user_to_group_updated(self):
        credentials = await self._new_credentials()
        username = credentials['username']
        token = await self._token('testuser')
        request = await self.client.put('/users/%s' % username,
                                        json={'groups': ['users']},
                                        token=token)
        data = self.json(request.response, 200)
        self.assertTrue('groups[]' in data)
        self.assertEqual(data['groups[]'], [{'id': 'users'}])
        #
        request = await self.client.put(
            '/users/%s' % username,
            json={'groups': ['users', 'power-users']},
            token=token
        )
        data = self.json(request.response, 200)
        self.assertTrue('groups[]' in data)
        self.assertEqual(data['groups[]'],
                         [{'id': 'users'}, {'id': 'power-users'}])
        #
        request = await self.client.put(
            '/users/%s' % username,
            json={'groups': []},
            token=token
        )
        data = self.json(request.response, 200)
        self.assertTrue('groups[]' in data)
        self.assertEqual(data['groups[]'], [])
