from urllib.parse import urlparse

from tests.oauth import OAuthTest, test


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
        token1 = await self._oauth_redirect('github')
        #
        # Lets try another redirect, this time the user is not created because
        # it exists already
        token2 = await self._oauth_redirect('github')
        self.assertNotEqual(token1.token, token2.token)
        self.assertEqual(token1.user_id, token2.user_id)

    async def _oauth_redirect(self, provider):
        request = await self.client.get('/oauth/github/redirect?code=dcshcvhd')
        response = request.response
        self.assertEqual(response.status_code, 302)
        cookie = self.cookie(request.response)
        self.assertTrue(cookie.startswith('test-oauth='))
        self.assertFalse(request.cache.user.is_authenticated())
        # Accessing the domain with the cookie yield an authenticated user
        request = await self.client.get('/', cookie=cookie)
        user = request.cache.user
        self.assertTrue(user.is_authenticated())
        return await self._test_token(user, 'github')

    @test.green
    def _test_token(self, user, provider):
        odm = self.app.odm()
        with odm.begin() as session:
            tokens = session.query(odm.accesstoken).filter_by(
                user_id=user.id, provider=provider).all()
            self.assertEqual(len(tokens), 1)
            token = tokens[0]
            self.assertTrue(len(token.token), 20)
            user = session.query(odm.user).get(user.id)
            self.assertTrue(user.oauth['github'])
            return token
