

class RegistrationMixin:
    """Test registration CRUD views
    """
    async def test_get_registrations_403(self):
        request = await self.client.get('/registrations')
        self.assertEqual(request.response.status_code, 403)

    async def test_get_registrations(self):
        token = await self._token()
        request = await self.client.get('/registrations', token=token)
        self.json(request.response, 200)

    async def test_options_registrations_metadata(self):
        request = await self.client.options('/registrations/metadata')
        self.checkOptions(request.response)

    async def test_get_registrations_metadata_403(self):
        request = await self.client.get('/registrations/metadata')
        self.assertEqual(request.response.status_code, 403)

    async def test_get_registrations_metadata(self):
        token = await self._token()
        request = await self.client.get('/registrations/metadata',
                                        token=token)
        self.json(request.response, 200)

    async def test_create_registration_405(self):
        request = await self.client.post('/registrations')
        self.json(request.response, 405)
