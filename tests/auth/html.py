from lux.utils import test

__test__ = False


class HtmlMixin:

    def test_html_login(self):
        request = yield from self.client.get('/login')
        html = self.html(request.response, 200)
        self.assertTrue(html)

    def test_html_test(self):
        request = yield from self.client.get('/test')
        bs = self.bs(request.response, 200)
        meta = bs.find_all('meta', attrs={'name': 'permission'})
        self.assertFalse(meta)

    def test_html_authenticated(self):
        # lets create a user
        username = test.randomname(prefix='u-')
        password = test.randomname()

        token = yield from self._token(self.su_credentials)

        data = {'username': username,
                'password': password,
                'password_repeat': password}
        #
        # Fail creation, missing email
        request = yield from self.client.post('/users',
                                              body=data,
                                              token=token,
                                              content_type='application/json')
        self.assertValidationError(request.response, 'email', 'required')
        #
        # Now create it
        data['email'] = '%s@%s.com' % (username, username)
        request = yield from self.client.post('/users',
                                              body=data,
                                              token=token,
                                              content_type='application/json')
        self.json(request.response, 201)
        #
        # Lets add user to 'secret-readers' group
        request = yield from self.client.get('/groups?name=secret-readers',
                                             token=token,
                                             content_type='application/json')
        data = self.json(request.response, 200)['result']
        self.assertEqual(len(data), 1)
        gid = data[0]['id']

        request = yield from self.client.post(
            '/users/%s' % username,
            body={'groups[]': [gid]},
            token=token,
            content_type='application/json')
        data = self.json(request.response, 200)
        groups = data['groups[]']
        self.assertEqual(len(groups), 1)

        # Finally we are ready to test the html view, lets login
        request = yield from self.client.get('/login')
        # cookie = self.cookie(request.response)
        # self.assertTrue(cookie)
        # request = yield from self.client.post('/login',
        #                                      body=dict(username=username,
        #                                                password=password),
        #                                      content_type='application/json',
        #                                      cookie=cookie)
        # self.json(request.response, 200)
