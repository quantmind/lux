

class PasswordMixin:

    async def test_get(self):
        request = await self.client.get('/')
        response = request.response
        self.assertEqual(response.status_code, 200)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())

    async def test_reset_password_errors(self):
        request = await self.client.post(self.api_url('passwords'),
                                         json={},
                                         token=self.pippo_token)
        self.json(request.response, 405)
        request = await self.client.post(self.api_url('passwords'),
                                         json={})
        self.json(request.response, 401)
        request = await self.client.post(self.api_url('passwords'),
                                         json={},
                                         jwt=self.admin_jwt)
        self.assertValidationError(request.response, 'email', 'required')

    async def test_reset_password(self):
        data = dict(email='toni@toni.com')
        request = await self.client.post(self.api_url('passwords'),
                                         jwt=self.admin_jwt,
                                         json=data)
        result = self.json(request.response, 201)
        self.assertEqual(result['user']['email'], data['email'])
        self.assertTrue(result['id'])
        #
        url = self.api_url('passwords/%s' % result['id'])
        request = await self.client.post(url, json={})
        self.json(request.response, 401)
        request = await self.client.post(url, json={}, jwt=self.admin_jwt)
        self.assertValidationError(request.response, 'password', 'required')
        data = {'password': 'newpassword',
                'password_repeat': 'newpassword'}
        request = await self.client.post(url, json=data, jwt=self.admin_jwt)
        self.assertTrue(self.json(request.response, 200)['success'])
        request = await self.client.post(url, json=data, jwt=self.admin_jwt)
        self.json(request.response, 404)


class d:

    async def test_login_fail(self):
        data = {'username': 'jdshvsjhvcsd',
                'password': 'dksjhvckjsahdvsf'}
        request = await self.client.post('/authorizations', json=data)
        self.assertValidationError(request.response,
                                   text='Invalid username or password')

    async def test_corrupted_token(self):
        '''Test the response when using a corrupted token
        '''
        request = await self.client.get('/secrets')
        self.assertEqual(request.response.status_code, 403)
        request = await self.client.get('/secrets', token=self.super_token)
        self.assertEqual(request.response.status_code, 200)
        badtoken = self.super_token[:-1]
        self.assertNotEqual(self.super_token, badtoken)
        request = await self.client.get('/secrets', token=badtoken)
        self.assertEqual(request.response.status_code, 400)
