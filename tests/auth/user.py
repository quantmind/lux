

class UserMixin:

    # User endpoints
    async def test_get_user_401(self):
        request = await self.client.get('/user')
        self.check401(request.response)

    async def test_get_user_200(self):
        token = await self._token('pippo')
        request = await self.client.get('/user', token=token)
        data = self.json(request.response, 200)
        self.assertEqual(data['username'], 'pippo')

    async def test_post_user_401(self):
        request = await self.client.post('/user', json=dict(name='gino'))
        self.check401(request.response)

    async def test_post_user_200(self):
        credentials = await self._new_credentials()
        token = await self._token(credentials)
        request = await self.client.post('/user',
                                         token=token,
                                         json=dict(first_name='gino'))
        data = self.json(request.response, 200)
        self.assertEqual(data['username'], credentials['username'])
        self.assertEqual(data['first_name'], 'gino')

    async def test_options_user_permissions(self):
        request = await self.client.options('/user/permissions')
        self.checkOptions(request.response)

    async def test_get_user_permissions_anonymous(self):
        request = await self.client.get('/user/permissions')
        response = request.response
        self.json(response, 200)

    async def test_get_user_permissions_200(self):
        token = await self._token('pippo')
        request = await self.client.get('/user/permissions', token=token)
        self.json(request.response, 200)
