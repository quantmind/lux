

class UserMixin:
    """Test autheticated user CRUD views
    """
    # User endpoints
    async def test_get_user_401(self):
        request = await self.client.get(self.api_url('user'))
        self.check401(request.response)

    async def test_get_user_200(self):
        request = await self.client.get(self.api_url('user'),
                                        token=self.pippo_token)
        data = self.json(request.response, 200)
        self.assertEqual(data['username'], 'pippo')

    async def test_update_user_401(self):
        request = await self.client.patch(self.api_url('user'),
                                          json=dict(name='gino'))
        self.check401(request.response)

    async def test_update_user_200(self):
        credentials = await self._new_credentials()
        token = await self.user_token(credentials,
                                      jwt=self.admin_jwt)
        request = await self.client.patch(self.api_url('user'),
                                          token=token,
                                          json=dict(first_name='gino'))
        data = self.json(request.response, 200)
        self.assertEqual(data['username'], credentials['username'])
        self.assertEqual(data['first_name'], 'gino')

    async def test_options_user_permissions(self):
        request = await self.client.options(self.api_url('user/permissions'))
        self.checkOptions(request.response)

    async def test_get_user_permissions_anonymous(self):
        request = await self.client.get(self.api_url('user/permissions'))
        response = request.response
        self.json(response, 200)

    async def test_get_user_permissions_200(self):
        request = await self.client.get(self.api_url('user/permissions'),
                                        token=self.pippo_token)
        self.json(request.response, 200)
