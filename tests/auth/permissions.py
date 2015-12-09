__test__ = False


class PermissionsMixin:

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
        self.assertValidationError(request.response, '',
                                   text='Policy empty')
        #
        data = dict(name='blabla', description='hgv hh', policy='67')
        request = yield from self.client.post('/permissions',
                                              body=data,
                                              content_type='application/json',
                                              token=token)
        self.assertValidationError(request.response, '',
                                   text='Policy should be a list or an object')
        #
        data = dict(name='blabla', description='hgv hh', policy='[45]')
        request = yield from self.client.post('/permissions',
                                              body=data,
                                              content_type='application/json',
                                              token=token)
        self.assertValidationError(request.response, '',
                                   text='Policy should be a list or an object')
        #
        data = dict(name='blabla', description='hgv hh', policy='{}')
        request = yield from self.client.post('/permissions',
                                              body=data,
                                              content_type='application/json',
                                              token=token)
        self.assertValidationError(request.response, '',
                                   text='"resource" must be defined')

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
