

class UserMixin:

    async def test_get_user_authkey_options(self):
        request = await self.client.options('/users/authkey')
        self.assertEqual(request.response.status_code, 200)

    async def test_get_user_authkey_404(self):
        request = await self.client.get('/users/authkey')
        self.json(request.response, 404)

    async def test_get_user_authkey_404_with_key(self):
        request = await self.client.get('/users/authkey?auth_key=foo')
        self.json(request.response, 404)

    async def __test_get_user_authkey_200(self):
        token = await self._token()
        request = await self.client.get('/users/authkey?auth_key=foo',
                                        token=token)
        data = self.json(request.response, 200)
        self.assertEqual(len(data['result']), 0)
