from urllib.parse import urlparse

from tests.oauth import test


class GithubMixin:

    # Github OAUTH
    async def __test_authorization_redirect(self):
        request = await self.client.get('/oauth/github')
        response = request.response
        self.assertEqual(response.status_code, 302)
        loc = urlparse(response['location'])
        self.assertTrue(loc.query)

    async def test_github_redirect_error(self):
        request = await self.client.get('/oauth/github/redirect')
        response = request.response
        self.assertEqual(response.status_code, 302)
        self.assertTrue(request.logger.exception.called)

    async def __test_github_redirect_user_created(self):
        token1 = await self._oauth_redirect('github')
        #
        # Lets try another redirect, this time the user is not created because
        # it exists already
        token2 = await self._oauth_redirect('github')
        self.assertNotEqual(token1.token, token2.token)
        self.assertEqual(token1.user_id, token2.user_id)

    async def _test_github_oauth_redirect(self, provider):
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
    def _test_github_token(self, user, provider):
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
