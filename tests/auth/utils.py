from lux.utils import test


class AuthUtils:
    """No tests, just utilities for testing auth module
    """
    async def _create_objective(self, token, subject='My objective', **data):
        data['subject'] = subject
        request = await self.client.post('/objectives', json=data, token=token)
        data = self.json(request.response, 201)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        self.assertEqual(data['subject'], subject)
        self.assertTrue('created' in data)
        return data

    @test.green
    def _new_credentials(self, username=None, superuser=False, active=True):
        backend = self.app.auth_backend
        request = self.app.wsgi_request()

        username = username or test.randomname()
        password = username
        email = '%s@test.com' % username

        user = backend.create_user(request,
                                   username=username,
                                   email=email,
                                   password=password,
                                   first_name=username,
                                   active=active)
        self.assertTrue(user.id)
        self.assertEqual(user.first_name, username)
        self.assertEqual(user.is_superuser(), superuser)
        self.assertEqual(user.is_active(), active)
        return {'username': username, 'password': password}

    async def _token(self, credentials):
        '''Return a token for a user
        '''
        if isinstance(credentials, str):
            credentials = {"username": credentials,
                           "password": credentials}

        # Get new token
        request = await self.client.post('/authorizations',
                                         json=credentials)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())
        data = self.json(request.response, 201)
        self.assertTrue('token' in data)
        return data['token']
