from lux.utils import test

import tests


class WebsiteTest(tests.AuthFixtureMixin, test.WebApiTestCase):
    config_file = 'example.webapi.config'
    web_config_file = 'example.website.config'

    async def _login(self, credentials=None, csrf=None, status=201):
        '''Return a token for a new superuser
        '''
        # We need csrf and cookie to successfully login
        cookie = None
        if csrf is None:
            request = await self.webclient.get('/auth/login')
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
            '/auth/login',
            content_type='application/json',
            body=credentials,
            cookie=cookie)
        data = self.json(request.response, status)
        if status == 201:
            cookie2 = self.cookie(request.response)
            self.assertTrue(cookie.startswith('test-website='))
            self.assertNotEqual(cookie, cookie2)
            self.assertFalse(request.cache.user.is_authenticated())
            self.assertTrue('token' in data)
            return cookie2, data['token']
