from tests import web


class AuthTest(web.WebsiteTest):

    async def test_html_signup(self):
        request = await self.webclient.get('/signup')
        html = self.html(request.response, 200)
        self.assertTrue(html)

    async def test_signup(self):
        data = await self._signup()
        self.assertTrue('email' in data)

    async def test_signup_error(self):
        data = {'username': 'djkhvbdf'}
        request = await self.webclient.post('/signup',
                                            body=data,
                                            content_type='application/json')
        self.json(request.response, 403)

    async def test_signup_error_api(self):
        data = {'username': 'djkhvbdf'}
        request = await self.client.post('/authorizations/signup',
                                         body=data,
                                         content_type='application/json')
        self.assertValidationError(request.response)

    async def test_signup_confirmation(self):
        data = await self._signup()
        reg = await self._get_registration(data['email'])
        self.assertTrue(reg.id)
        request = await self.webclient.get('/signup/%s' % reg.id)
        doc = self.bs(request.response, 200)
        body = doc.find('body')
        self.assertTrue(body)
        # await self._check_body(reg, body)

    async def _(self, reg, body):
        login = body.find_all('a')
        self.assertEqual(len(login), 1)
        text = login[0].prettify()
        self.assertTrue(self.app.config['LOGIN_URL'] in text)
        text = body.get_text()
        self.assertTrue('You have confirmed your email' in text)
        request = await self.client.get('/signup/%s' % reg.id)
        html = self.html(request.response, 410)
        self.assertTrue(html)

    async def __test_confirm_signup(self):
        data = await self._signup()
        reg = await self.app.green_pool.submit(self._get_registration,
                                               data['email'])
        api_url = '/authorizations/signup/%s' % reg.id
        request = await self.client.options(api_url)
        self.assertEqual(request.response.status_code, 200)
        #
        request = await self.client.post(api_url)
        data = self.json(request.response, 200)
        self.assertTrue(data['success'])
        request = await self.client.post(api_url)
        self.json(request.response, 410)
