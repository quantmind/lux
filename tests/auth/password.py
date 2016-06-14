

class PasswordMixin:

    async def test_get(self):
        request = await self.client.get('/')
        response = request.response
        self.assertEqual(response.status_code, 200)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())

    async def test_reset_password_errors(self):
        token = await self._token('pippo')
        request = await self.client.post('/authorizations/reset-password',
                                         json={},
                                         token=token)
        # user is authenticated, method not allowed
        self.json(request.response, 405)
        request = await self.client.post('/authorizations/reset-password',
                                         json={})
        self.assertValidationError(request.response)

    async def test_reset_password_200(self):
        data = dict(email='toni@toni.com')
        request = await self.client.post('/authorizations/reset-password',
                                         json=data)
        self.json(request.response, 200)

    async def test_login_fail(self):
        data = {'username': 'jdshvsjhvcsd',
                'password': 'dksjhvckjsahdvsf'}
        request = await self.client.post('/authorizations', json=data)
        self.assertValidationError(request.response,
                                   text='Invalid username or password')

    async def test_corrupted_token(self):
        '''Test the response when using a corrupted token
        '''
        token = await self._token('testuser')
        request = await self.client.get('/secrets')
        self.assertEqual(request.response.status_code, 403)
        request = await self.client.get('/secrets', token=token)
        self.assertEqual(request.response.status_code, 200)
        badtoken = token[:-1]
        self.assertNotEqual(token, badtoken)
        request = await self.client.get('/secrets', token=badtoken)
        self.assertEqual(request.response.status_code, 401)
