from lux.utils import test


class AuthUtils:
    """No tests, just utilities for testing auth module
    """
    async def _create_objective(self, token, subject='My objective', **data):
        data['subject'] = subject
        request = await self.client.post(
            '/objectives', body=data, token=token,
            content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 201)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        self.assertEqual(data['subject'], subject)
        self.assertTrue('created' in data)
        return data

    async def _new_credentials(self):
        username = test.randomname()
        password = test.randomname()

        credentials = {
            'username': username,
            'password': password
        }

        email = '%s@%s.com' % (username, test.randomname())
        user = await self.create_superuser(username, email, password)
        self.assertEqual(user.username, username)
        self.assertNotEqual(user.password, password)
        return credentials

    async def _token(self, credentials=None):
        '''Return a token for a new superuser
        '''
        if credentials is None:
            credentials = await self._new_credentials()

        # Get new token
        request = await self.client.post('/authorizations',
                                         json=credentials)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())
        data = self.json(request.response, 201)
        self.assertTrue('token' in data)
        return data['token']
