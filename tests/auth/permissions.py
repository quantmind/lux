

class PermissionsMixin:

    async def test_group_validation(self):
        token = await self._token()
        payload = {'name': 'abc'}
        request = await self.client.post('/groups',
                                         body=payload,
                                         content_type='application/json',
                                         token=token)
        data = self.json(request.response, 201)
        gid = data['id']
        payload['name'] = 'abcd'
        request = await self.client.post('/groups/{}'.format(gid),
                                         body=payload,
                                         content_type='application/json',
                                         token=token)

        data = self.json(request.response, 200)
        self.assertEqual(data['name'], 'abcd')
        self.assertEqual(data['id'], gid)

        payload['name'] = 'ABCd'
        request = await self.client.post('/groups',
                                         body=payload,
                                         content_type='application/json',
                                         token=token)

        self.assertValidationError(request.response, 'name',
                                   'Only lower case, alphanumeric characters '
                                   'and hyphens are allowed')

    async def test_create_permission_errors(self):
        token = await self._token()
        request = await self.client.post('/permissions',
                                         json=dict(name='blabla'),
                                         token=token)
        self.assertValidationError(request.response, 'policy', 'required')
        #
        data = dict(name='blabla', policy='{')
        request = await self.client.post('/permissions',
                                         body=data,
                                         content_type='application/json',
                                         token=token)
        self.assertValidationError(request.response, 'policy',
                                   'not a valid JSON string')
        #
        data = dict(name='blabla', description='hgv hh', policy='[]')
        request = await self.client.post('/permissions',
                                         body=data,
                                         content_type='application/json',
                                         token=token)
        self.assertValidationError(request.response, '',
                                   text='Policy empty')
        #
        data = dict(name='blabla', description='hgv hh', policy='67')
        request = await self.client.post('/permissions',
                                         body=data,
                                         content_type='application/json',
                                         token=token)
        self.assertValidationError(request.response, '',
                                   text='Policy should be a list or an object')
        #
        data = dict(name='blabla', description='hgv hh', policy='[45]')
        request = await self.client.post('/permissions',
                                         body=data,
                                         content_type='application/json',
                                         token=token)
        self.assertValidationError(request.response, '',
                                   text='Policy should be a list or an object')
        #
        data = dict(name='blabla', description='hgv hh', policy='{}')
        request = await self.client.post('/permissions',
                                         body=data,
                                         content_type='application/json',
                                         token=token)
        self.assertValidationError(request.response, '',
                                   text='"resource" must be defined')

    async def test_column_permissions_read(self):
        """Tests read requests against columns with permission level 0"""
        su_token = await self._token(self.su_credentials)

        objective = await self._create_objective(su_token)

        request = await self.client.get(
            '/objectives/{}'.format(objective['id']))
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertFalse('subject' in data)

        request = await self.client.get('/objectives')
        data = self.json(request.response, 200)
        self.assertTrue('result' in data)
        for item in data['result']:
            self.assertTrue('id' in item)
            self.assertFalse('subject' in item)

        request = await self.client.get('/objectives/metadata')
        data = self.json(request.response, 200)
        self.assertFalse(
            any(field['name'] == 'subject' for field in data['columns']))

        request = await self.client.get(
            '/objectives/{}'.format(objective['id']), token=su_token)
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('subject' in data)

        request = await self.client.get(
            '/objectives', token=su_token)
        data = self.json(request.response, 200)
        self.assertTrue('result' in data)
        for item in data['result']:
            self.assertTrue('id' in item)
            if item['id'] == objective['id']:
                self.assertTrue('subject' in item)

        request = await self.client.get(
            '/objectives/metadata', token=su_token)
        data = self.json(request.response, 200)
        self.assertTrue(
            any(field['name'] == 'subject' for field in data['columns']))

    async def test_column_permissions_update_create(self):
        """
        Tests create and update requests against columns
        with permission levels 10 and 20
        """
        su_token = await self._token(self.su_credentials)

        objective = await self._create_objective(su_token,
                                                 deadline="next week",
                                                 outcome="under achieved")
        self.assertTrue('deadline' in objective)
        self.assertTrue('outcome' in objective)

        request = await self.client.post(
            '/objectives/{}'.format(objective['id']),
            content_type='application/json',
            body={
                'deadline': 'end of May',
                'outcome': 'exceeded'
            })
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('outcome' in data)
        self.assertEqual(data['outcome'], "under achieved")
        self.assertTrue('deadline' in data)
        self.assertEqual(data['deadline'], "end of May")

        request = await self.client.get(
            '/objectives/{}'.format(objective['id']), token=su_token)
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('subject' in data)
        self.assertTrue('outcome' in data)
        self.assertTrue('deadline' in data)
        self.assertEqual(data['deadline'], "end of May")
        self.assertEqual(data['outcome'], "under achieved")

    async def test_column_permissions_policy(self):
        """
        Checks that a custom policy works on a column with default access
        level 0
        """
        user_token = await self._token(self.user_credentials)

        objective = await self._create_objective(user_token)

        request = await self.client.get(
            '/objectives/{}'.format(objective['id']), token=user_token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue('id' in data)
        self.assertTrue('subject' in data)

        request = await self.client.get(
            '/objectives', token=user_token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue('result' in data)
        for item in data['result']:
            self.assertTrue('id' in item)
            self.assertTrue('subject' in item)

        request = await self.client.get(
            '/objectives/metadata', token=user_token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertTrue(
            any(field['name'] == 'subject' for field in data['columns']))

        request = await self.client.post(
            '/objectives/{}'.format(objective['id']),
            content_type='application/json',
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

    async def test_add_user_to_group(self):
        credentials = await self._new_credentials()
        username = credentials['username']
        token = await self._token(credentials)
        request = await self.client.put('/users/%s' % username,
                                        body={'groups[]': [1]},
                                        content_type='application/json',
                                        token=token)
        data = self.json(request.response, 200)
        self.assertTrue('groups[]' in data)
