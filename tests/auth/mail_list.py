
class MailListMixin:

    async def test_mailing_list_options(self):
        request = await self.client.options(self.api_url('mailinglist'))
        self.checkOptions(request.response, ['GET', 'POST', 'HEAD'])

    async def test_mailing_list_post_422(self):
        request = await self.client.post(
            self.api_url('mailinglist'),
            json={},
            jwt=self.admin_jwt
        )
        self.assertValidationError(request.response, 'email')

    async def test_mailing_list_post(self):
        request = await self.client.post(
            self.api_url('mailinglist'),
            json=dict(email='foo@foo.com', topic='general'),
            jwt=self.admin_jwt
        )
        data = self.json(request.response, 201)
        self.assertTrue(data)
        request = await self.client.post(
            self.api_url('mailinglist'),
            json=dict(email='foo@foo.com'),
            jwt=self.admin_jwt
        )
        self.assertValidationError(request.response, text='Already subscribed')
