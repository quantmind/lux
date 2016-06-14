from lux.utils import test

from tests.auth.utils import AuthUtils


class TestPermissions(test.AppTestCase, AuthUtils):
    config_file = 'tests.auth'

    async def test_anonymous_get_200(self):
        request = await self.client.get('/objectives')
        data = self.json(request.response, 200)
        self.assertTrue(data['result'])

    async def test_anonymous_get_403(self):
        request = await self.client.get('/secrets')
        self.json(request.response, 403)
        request = await self.client.get('/users')
        self.json(request.response, 403)

    async def test_users_group_get_200(self):
        token = await self._token("pippo")
        request = await self.client.get('/users', token=token)
        data = self.json(request.response, 200)
        self.assertTrue(data['result'])
        for user in data['result']:
            self.assertFalse('groups' in user)
            self.assertFalse('superuser' in user)

    async def test_users_group_get_403(self):
        token = await self._token("pippo")
        request = await self.client.get('/secrets', token=token)
        self.json(request.response, 403)
        request = await self.client.get('/permissions', token=token)
        self.json(request.response, 403)

    async def test_policy_makers_get_200(self):
        token = await self._token("toni")
        request = await self.client.get('/permissions', token=token)
        self.json(request.response, 200)

    async def test_policy_makers_update_200(self):
        token = await self._token("toni")
        descr = 'Can view everything from secrets, users and groups'
        request = await self.client.post(
            '/permissions/read-secrets-users-groups',
            json=dict(description=descr),
            token=token)
        data = self.json(request.response, 200)
        self.assertEqual(data['description'], descr)

    async def test_policy_makers_delete_403(self):
        token = await self._token("toni")
        request = await self.client.delete(
            '/permissions/read-secrets-users-groups',
            token=token)
        self.assertEqual(request.response.status_code, 403)
