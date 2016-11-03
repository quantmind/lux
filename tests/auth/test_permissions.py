from asyncio import gather

from lux.utils import test

from tests.auth.utils import AuthUtils, deadline


class TestPermissions(test.AppTestCase, AuthUtils):
    """Test user permissions
    """
    config_file = 'tests.auth'

    @classmethod
    async def beforeAll(cls):
        cls.super_token, cls.toni_token, cls.pippo_token = await gather(
            cls.user_token('testuser', jwt=cls.admin_jwt),
            cls.user_token('toni', jwt=cls.admin_jwt),
            cls.user_token('pippo', jwt=cls.admin_jwt)
        )

    async def test_anonymous_get_200(self):
        request = await self.client.get('/objectives')
        data = self.json(request.response, 200)
        self.assertTrue(data['result'])

    async def test_anonymous_get_401(self):
        request = await self.client.get('/secrets')
        self.json(request.response, 401)
        request = await self.client.get('/users')
        self.json(request.response, 401)

    async def test_users_group_get_200(self):
        request = await self.client.get('/users', token=self.toni_token)
        data = self.json(request.response, 200)
        self.assertTrue(data['result'])
        for user in data['result']:
            self.assertFalse('groups' in user)
            self.assertFalse('superuser' in user)

    async def test_users_group_get_403(self):
        request = await self.client.get('/secrets', token=self.pippo_token)
        self.json(request.response, 403)
        request = await self.client.get('/permissions', token=self.pippo_token)
        self.json(request.response, 403)

    async def test_policy_makers_get_200(self):
        request = await self.client.get('/permissions', token=self.toni_token)
        self.json(request.response, 200)

    async def test_policy_makers_update_200(self):
        descr = 'Can view everything from secrets, users and groups'
        request = await self.client.patch(
            '/permissions/read-secrets-users-groups',
            json=dict(description=descr),
            token=self.toni_token
        )
        data = self.json(request.response, 200)
        self.assertEqual(data['description'], descr)

    async def test_policy_makers_delete_403(self):
        request = await self.client.delete(
            '/permissions/read-secrets-users-groups',
            token=self.toni_token
        )
        self.assertEqual(request.response.status_code, 403)

    async def test_column_permissions_read(self):
        """Tests read requests against columns with permission level 0"""
        objective = await self._create_objective(self.super_token)

        request = await self.client.get(
            '/objectives/{}'.format(objective['id']))
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertFalse('deadline' in data)

        request = await self.client.get('/objectives')
        data = self.json(request.response, 200)
        self.assertTrue('result' in data)
        for item in data['result']:
            self.assertTrue('id' in item)
            self.assertFalse('deadline' in item)

        request = await self.client.get('/objectives/metadata')
        data = self.json(request.response, 200)
        self.assertFalse(
            any(field['name'] == 'deadline' for field in data['columns']))

        request = await self.client.get(
            '/objectives/{}'.format(objective['id']),
            token=self.super_token
        )
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('deadline' in data)

        request = await self.client.get(
            '/objectives', token=self.super_token
        )
        data = self.json(request.response, 200)
        self.assertTrue('result' in data)
        for item in data['result']:
            self.assertTrue('id' in item)
            if item['id'] == objective['id']:
                self.assertTrue('deadline' in item)

        request = await self.client.get(
            '/objectives/metadata', token=self.super_token
        )
        data = self.json(request.response, 200)
        self.assertTrue(
            any(field['name'] == 'deadline' for field in data['columns']))

    async def test_column_permissions_update_create(self):
        """
        Tests create and update requests against columns
        with permission levels 10 and 20
        """
        objective = await self._create_objective(self.super_token,
                                                 outcome="under achieved")
        self.assertTrue('deadline' in objective)
        self.assertTrue('outcome' in objective)

        request = await self.client.patch(
            self.api_url('objectives/%s' % objective['id']),
            json={
                'deadline': deadline(20),
                'outcome': 'exceeded'
            })
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('outcome' in data)
        self.assertEqual(data['outcome'], "exceeded")
        self.assertFalse('deadline' in data)

        request = await self.client.get(
            self.api_url('objectives/%s' % objective['id']),
            token=self.super_token
        )
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('subject' in data)
        self.assertTrue('outcome' in data)
        self.assertTrue('deadline' in data)
        self.assertEqual(data['deadline'], deadline(10))
        self.assertEqual(data['outcome'], "exceeded")

    async def test_column_permissions_policy(self):
        """Checks that a custom policy works on a regular user
        """
        objective = await self._create_objective(self.pippo_token)

        request = await self.client.get(
            self.api_url('objectives/%s' % objective['id']),
            token=self.pippo_token
        )
        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('subject' in data)

        request = await self.client.get(
            self.api_url('objectives'),
            token=self.pippo_token
        )
        data = self.json(request.response, 200)
        self.assertTrue('result' in data)
        for item in data['result']:
            self.assertTrue('id' in item)
            self.assertTrue('subject' in item)

        request = await self.client.get(
            self.api_url('objectives/metadata'),
            token=self.pippo_token
        )
        data = self.json(request.response, 200)
        self.assertTrue(
            any(field['name'] == 'deadline' for field in data['columns'])
        )

        # Patch the model
        request = await self.client.patch(
            self.api_url('objectives/%s' % objective['id']),
            token=self.pippo_token,
            json={'subject': 'subject changed',
                  'deadline': deadline(20)}
        )

        data = self.json(request.response, 200)
        self.assertTrue('id' in data)
        self.assertTrue('deadline' in data)
        self.assertEqual(data['deadline'], deadline(20))
        self.assertEqual(data['subject'], "subject changed")
