from lux.utils import test

__test__ = False


class PasswordMixin:

    def test_backend(self):
        backend = self.app.auth_backend
        self.assertTrue(backend)
        self.assertTrue(backend.backends)

    @test.green
    def test_get_user_none(self):
        backend = self.app.auth_backend
        request = self.app.wsgi_request()
        user = backend.get_user(request, user_id=18098098)
        self.assertEqual(user, None)
        user = backend.get_user(request, email='ksdcks.sdvddvf@djdjhdfc.com')
        self.assertEqual(user, None)
        user = backend.get_user(request, username='dhvfvhsdfgvhfd')
        self.assertEqual(user, None)

    @test.green
    def test_create_user(self):
        backend = self.app.auth_backend
        request = self.app.wsgi_request()

        user = backend.create_user(request,
                                   username='pippo',
                                   email='pippo@pippo.com',
                                   password='pluto',
                                   first_name='Pippo')
        self.assertTrue(user.id)
        self.assertEqual(user.first_name, 'Pippo')
        self.assertFalse(user.is_superuser())
        self.assertFalse(user.is_active())

        # make it active
        with self.app.odm().begin() as session:
            user.active = True
            session.add(user)

        self.assertTrue(user.is_active())

    @test.green
    def test_create_superuser(self):
        backend = self.app.auth_backend
        request = self.app.wsgi_request()

        user = backend.create_superuser(request,
                                        username='foo',
                                        email='foo@pippo.com',
                                        password='pluto',
                                        first_name='Foo')
        self.assertTrue(user.id)
        self.assertEqual(user.first_name, 'Foo')
        self.assertTrue(user.is_superuser())
        self.assertTrue(user.is_active())

    @test.green
    def test_permissions(self):
        '''Test permission models
        '''
        odm = self.app.odm()

        with odm.begin() as session:
            user = odm.user(username=test.randomname())
            group = odm.group(name='staff')
            session.add(user)
            session.add(group)
            group.users.append(user)

        self.assertTrue(user.id)
        self.assertTrue(group.id)

        groups = user.groups
        self.assertTrue(group in groups)

        with odm.begin() as session:
            # add goup to the session
            session.add(group)
            permission = odm.permission(name='admin',
                                        description='Can access the admin',
                                        policy={})
            group.permissions.append(permission)

    # REST API
    def test_get(self):
        request = yield from self.client.get('/')
        response = request.response
        self.assertEqual(response.status_code, 200)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())

    # REST - GROUPS
    def test_group_validation(self):
        token = yield from self._token()
        payload = {'name': 'abc'}
        request = yield from self.client.post('/groups',
                                              body=payload,
                                              content_type='application/json',
                                              token=token)
        data = self.json(request.response, 201)
        gid = data['id']
        payload['name'] = 'abcd'
        request = yield from self.client.post('/groups/{}'.format(gid),
                                              body=payload,
                                              content_type='application/json',
                                              token=token)

        data = self.json(request.response, 200)
        self.assertEqual(data['name'], 'abcd')
        self.assertEqual(data['id'], gid)

        payload['name'] = 'ABCd'
        request = yield from self.client.post('/groups',
                                              body=payload,
                                              content_type='application/json',
                                              token=token)

        self.assertValidationError(request.response, 'name',
                                   'Only lower case, alphanumeric characters '
                                   'and hyphens are allowed')

    def test_login_fail(self):
        data = {'username': 'jdshvsjhvcsd',
                'password': 'dksjhvckjsahdvsf'}
        request = yield from self.client.post('/authorizations',
                                              content_type='application/json',
                                              body=data)
        data = self.json(request.response, 422)
        self.assertEqual(data['message'], 'Invalid username or password')
        self.assertEqual(data['status'], 422)

    def test_create_superuser_command_and_token(self):
        return self._token()

    def test_create_permission_errors(self):
        token = yield from self._token()
        data = dict(name='blabla')
        request = yield from self.client.post('/permissions',
                                              body=data,
                                              content_type='application/json',
                                              token=token)
        self.assertValidationError(request.response, 'policy', 'required')
        #
        data = dict(name='blabla', policy='{')
        request = yield from self.client.post('/permissions',
                                              body=data,
                                              content_type='application/json',
                                              token=token)
        self.assertValidationError(request.response, 'policy',
                                   'not a valid JSON string')
        #
        data = dict(name='blabla', description='hgv hh', policy='[]')
        request = yield from self.client.post('/permissions',
                                              body=data,
                                              content_type='application/json',
                                              token=token)
        self.assertValidationError(request.response, text='Policy empty')
        #
        data = dict(name='blabla', description='hgv hh', policy='67')
        request = yield from self.client.post('/permissions',
                                              body=data,
                                              content_type='application/json',
                                              token=token)
        self.assertValidationError(request.response,
                                   text='Policy should be a list or an object')
        #
        data = dict(name='blabla', description='hgv hh', policy='[45]')
        request = yield from self.client.post('/permissions',
                                              body=data,
                                              content_type='application/json',
                                              token=token)
        self.assertValidationError(request.response,
                                   text='Policy should be a list or an object')
        #
        data = dict(name='blabla', description='hgv hh', policy='{}')
        request = yield from self.client.post('/permissions',
                                              body=data,
                                              content_type='application/json',
                                              token=token)
        self.assertValidationError(request.response,
                                   text='"action" must be defined')

    def test_column_permissions_read(self):
        """Tests read requests against columns with permission level 0"""
        su_token = yield from self._token(self.su_credentials)

        objective = yield from self._create_objective(su_token)

        request = yield from self.client.get(
            '/objectives/{}'.format(objective['id']))
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertFalse('subject' in data)

        request = yield from self.client.get(
            '/objectives')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue('result' in data)
        for item in data['result']:
            self.assertTrue('id' in item)
            self.assertFalse('subject' in item)

        request = yield from self.client.get(
            '/objectives/metadata')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertFalse(
            any(field['name'] == 'subject' for field in data['columns']))

        request = yield from self.client.get(
            '/objectives/{}'.format(objective['id']), token=su_token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue('id' in data)
        self.assertTrue('subject' in data)

        request = yield from self.client.get(
            '/objectives', token=su_token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue('result' in data)
        for item in data['result']:
            self.assertTrue('id' in item)
            if item['id'] == objective['id']:
                self.assertTrue('subject' in item)

        request = yield from self.client.get(
            '/objectives/metadata', token=su_token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue(
            any(field['name'] == 'subject' for field in data['columns']))

    def test_column_permissions_update_create(self):
        """
        Tests create and update requests against columns
        with permission levels 10 and 20
        """
        su_token = yield from self._token(self.su_credentials)

        objective = yield from self._create_objective(su_token,
                                                      deadline="next week",
                                                      outcome="under achieved")
        self.assertTrue('deadline' in objective)
        self.assertTrue('outcome' in objective)

        request = yield from self.client.post(
            '/objectives/{}'.format(objective['id']),
            body={
                'deadline': 'end of May',
                'outcome': 'exceeded'
            })

        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue('id' in data)
        self.assertTrue('outcome' in data)
        self.assertEqual(data['outcome'], "under achieved")
        self.assertTrue('deadline' in data)
        self.assertEqual(data['deadline'], "end of May")

        request = yield from self.client.get(
            '/objectives/{}'.format(objective['id']), token=su_token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue('id' in data)
        self.assertTrue('subject' in data)
        self.assertTrue('outcome' in data)
        self.assertTrue('deadline' in data)
        self.assertEqual(data['deadline'], "end of May")
        self.assertEqual(data['outcome'], "under achieved")

    def test_column_permissions_policy(self):
        """
        Checks that a custom policy works on a column with default access
        level 0
        """
        user_token = yield from self._token(self.user_credentials)

        objective = yield from self._create_objective(user_token)

        request = yield from self.client.get(
            '/objectives/{}'.format(objective['id']), token=user_token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue('id' in data)
        self.assertTrue('subject' in data)

        request = yield from self.client.get(
            '/objectives', token=user_token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue('result' in data)
        for item in data['result']:
            self.assertTrue('id' in item)
            self.assertTrue('subject' in item)

        request = yield from self.client.get(
            '/objectives/metadata', token=user_token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue(
            any(field['name'] == 'subject' for field in data['columns']))

        request = yield from self.client.post(
            '/objectives/{}'.format(objective['id']),
            token=user_token,
            body={
                'subject': 'subject changed'
            })

        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue('id' in data)
        self.assertTrue('subject' in data)
        self.assertEqual(data['subject'], "subject changed")

    def test_add_user_to_group(self):
        credentials = yield from self._new_credentials()
        username = credentials['username']
        token = yield from self._token(credentials)
        request = yield from self.client.put('/users/%s' % username,
                                             body={'groups[]': [1]},
                                             content_type='application/json',
                                             token=token)
        data = self.json(request.response, 200)
        self.assertTrue('groups[]' in data)

    def test_corrupted_token(self):
        '''Test the response when using a corrupted token
        '''
        token = yield from self._token()
        request = yield from self.client.get('/secrets')
        self.assertEqual(request.response.status_code, 403)
        request = yield from self.client.get('/secrets', token=token)
        self.assertEqual(request.response.status_code, 200)
        badtoken = token[:-1]
        self.assertNotEqual(token, badtoken)
        request = yield from self.client.get('/secrets', token=badtoken)
        self.assertEqual(request.response.status_code, 403)
