

class AuthenticationsMixin:

    # User endpoints
    async def test_authenticate(self):
        request = await self.client.get('/user')
        self.check401(request.response)
