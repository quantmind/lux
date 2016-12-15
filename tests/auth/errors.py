

class ErrorsMixin:
    """Test for errors in corner case situations
    """
    async def test_bad_authentication(self):
        request = await self.client.get(
            self.api_url('user'),
            headers=[('Authorization', 'bjchdbjshbcjd')]
        )
        self.json(request.response, 400)
