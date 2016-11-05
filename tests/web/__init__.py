import os

from lux.utils import test


class WebsiteTest(test.WebApiTestCase):
    fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures')
    config_file = 'example.webapi.config'
    web_config_file = 'example.website.config'

    async def _login(self, credentials=None, csrf=None):
        '''Return a token for a new superuser
        '''
        # We need csrf and cookie to successfully login
        cookie = None
        if csrf is None:
            request = await self.webclient.get('/login')
            bs = self.bs(request.response, 200)
            csrf = self.authenticity_token(bs)
            cookie = self.cookie(request.response)
            self.assertTrue(cookie.startswith('test-website='))
        csrf = csrf or {}
        if credentials is None:
            credentials = 'testuser'
        if not isinstance(credentials, dict):
            credentials = dict(username=credentials,
                               password=credentials)
        credentials.update(csrf)

        # Get new token
        request = await self.webclient.post(
            '/login',
            json=credentials,
            cookie=cookie
        )
        self.assertTrue(self.json(request.response, 200)['success'])
        cookie2 = self.cookie(request.response)
        self.assertTrue(cookie.startswith('test-website='))
        self.assertNotEqual(cookie, cookie2)
        self.assertFalse(request.cache.user.is_authenticated())
        return cookie2
