__test__ = False


class PasswordMixin:

    def test_get(self):
        request = yield from self.client.get('/')
        response = request.response
        self.assertEqual(response.status_code, 200)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())

    def test_reset_password_errors(self):
        token = yield from self._token()
        request = yield from self.client.post('/authorizations/reset-password',
                                              body={},
                                              content_type='application/json',
                                              token=token)
        # user is authenticated, method not allowed
        self.json(request.response, 405)
        request = yield from self.client.post('/authorizations/reset-password',
                                              body={},
                                              content_type='application/json')
        self.assertValidationError(request.response)

    def test_reset_password_200(self):
        data = dict(email='bigpippo@pluto.com')
        request = yield from self.client.post('/authorizations/reset-password',
                                              body=data,
                                              content_type='application/json')
        self.json(request.response, 200)

    def test_login_fail(self):
        data = {'username': 'jdshvsjhvcsd',
                'password': 'dksjhvckjsahdvsf'}
        request = yield from self.client.post('/authorizations',
                                              content_type='application/json',
                                              body=data)
        self.assertValidationError(request.response,
                                   text='Invalid username or password')

    def test_create_superuser_command_and_token(self):
        return self._token()

    def test_corrupted_token(self):
        '''Test the response when using a corrupted token
        '''
        token = yield from self._token()
        request = yield from self.client.get('/secrets')
        self.assertEqual(request.response.status_code, 403)
        request = yield from self.client.get('/secrets', token=token)
        self.assertEqual(request.response.status_code, 200)
        badtoken = token[:-1]
        self.assertNotEqual(token, badtoken)
        request = yield from self.client.get('/secrets', token=badtoken)
        self.assertEqual(request.response.status_code, 401)
