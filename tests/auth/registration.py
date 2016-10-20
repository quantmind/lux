

class RegistrationMixin:
    """Test registration CRUD views
    """
    # Create new registration

    async def test_post_registrations_401(self):
        request = await self.client.post('/registrations', json={})
        self.assertEqual(request.response.status_code, 401)

    async def test_post_registrations_200(self):
        """Register a new user"""
        request = await self.client.post(
            '/registrations',
            json={"username": "fantozzi",
                  "password": "fantozzi",
                  "password_repeat": "fantozzi",
                  "email": "fantozzi@test.org"},
            jwt=self.admin_jwt
        )
        reg = self.json(request.response, 201)
        self.assertTrue(reg['id'])
        self.assertTrue(reg['expiry'])
        self.assertTrue(reg['user'])
        self.assertEqual(reg['user']['email'], 'fantozzi@test.org')
        self.assertEqual(reg['user']['active'], False)
        #
        # activate
        url = '/registrations/%s/activate' % reg['id']
        request = await self.client.post(url)
        self.json(request.response, 401)
        request = await self.client.post(url, token=self.super_token)
        self.json(request.response, 400)
        request = await self.client.post(url, jwt=self.admin_jwt)
        self.assertEqual(request.response.status_code, 204)

        request = await self.client.post(url, jwt=self.admin_jwt)
        self.json(request.response, 404)

    async def test_post_registrations_400(self):
        request = await self.client.post('/registrations', json={},
                                         jwt='sdjhvsjchsd')
        self.assertEqual(request.response.status_code, 400)

    # Get registrations

    async def test_get_registrations(self):
        """Test list of registrations"""
        request = await self.client.get('/registrations',
                                        token=self.super_token)
        self.json(request.response, 200)

    # Metadata

    async def test_options_registrations_metadata(self):
        request = await self.client.options('/registrations/metadata')
        self.checkOptions(request.response)

    async def test_get_registrations_metadata_401(self):
        request = await self.client.get('/registrations/metadata')
        self.assertEqual(request.response.status_code, 401)

    async def test_get_registrations_metadata_200(self):
        request = await self.client.get('/registrations/metadata',
                                        token=self.super_token)
        self.json(request.response, 200)

    async def test_get_registrations_metadata_403(self):
        request = await self.client.get('/registrations/metadata',
                                        token=self.pippo_token)
        self.json(request.response, 403)
