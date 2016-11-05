import asyncio

from tests import web


class AuthTest(web.WebsiteTest):
    web_config_params = dict(SESSION_EXPIRY=5)

    def test_apps(self):
        self.assertEqual(self.web.meta.name, 'example.website')
        self.assertEqual(self.app.meta.name, 'example.webapi')

    async def test_get_login(self):
        request = await self.webclient.get('/login')
        bs = self.bs(request.response, 200)
        self.assertEqual(str(bs.title), '<title>website.com</title>')

    async def test_login_fail(self):
        request = await self.webclient.get('/login')
        bs = self.bs(request.response, 200)
        credentials = self.authenticity_token(bs)
        cookie = self.cookie(request.response)
        credentials['username'] = 'xbjhxbhxs'
        credentials['password'] = 'sdcsacccscd'
        request = await self.webclient.post('/login',
                                            json=credentials,
                                            cookie=cookie)
        self.assertValidationError(request.response,
                                   text='Invalid credentials')

    async def test_login(self):
        await self._login()

    async def test_authenticated_view(self):
        cookie = await self._login()
        request = await self.webclient.get('/', cookie=cookie)
        self.bs(request.response, 200)
        self.assertTrue(request.cache.user.is_authenticated())
        self.assertFalse(request.response.cookies)

    async def test_invalid_authenticated_view(self):
        cookie = await self._login()
        request = await self.webclient.get('/', cookie=cookie)
        self.bs(request.response, 200)
        self.assertTrue(request.cache.user.is_authenticated())
        self.assertFalse(request.response.cookies)
        # Wait for 5 seconds
        await asyncio.sleep(self.web.config['SESSION_EXPIRY']+1)
        # The session is now expired
        request = await self.webclient.get('/', cookie=cookie)
        self.assertFalse(request.cache.user.is_authenticated())
