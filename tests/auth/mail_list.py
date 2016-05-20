url = '/authorizations/mailing-list'


class MailListMixin:

    async def test_mailing_list_options(self):
        request = await self.client.options(url)
        self.checkOptions(request.response, ['POST'])

    async def test_mailing_list_post_422(self):
        request = await self.client.post(url, json={})
        self.assertValidationError(request.response, 'email')

    async def test_mailing_list_post(self):
        request = await self.client.post(url,
                                         json=dict(email='foo@foo.com'))
        data = self.json(request.response, 201)
        self.assertTrue(data)
        request = await self.client.post(url,
                                         json=dict(email='foo@foo.com'))
        data = self.json(request.response, 200)
        self.assertTrue(data)
