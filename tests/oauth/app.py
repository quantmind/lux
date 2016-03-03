from urllib.parse import urlparse

from . import OAuthTest


class TestGithub(OAuthTest):

    async def test_oauths(self):
        request = await self.client.get('/')
        oauths = request.cache.oauths
        self.assertTrue(oauths)

    async def test_authorization_redirect(self):
        request = await self.client.get('/oauth/github')
        response = request.response
        self.assertEqual(response.status_code, 302)
        loc = urlparse(response['location'])
        self.assertTrue(loc.query)

    async def test_redirect_error(self):
        request = await self.client.get('/oauth/github/redirect')
        response = request.response
        self.assertEqual(response.status_code, 302)
        self.assertTrue(request.logger.exception.called)

    async def test_redirect_user_created(self):
        request = await self.client.get('/oauth/github/redirect?code=dcshcvhd')
        response = request.response
        self.assertEqual(response.status_code, 201)
