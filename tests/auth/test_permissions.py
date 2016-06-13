from lux.utils import test

from tests.auth.utils import AuthUtils


class TestPermissions(test.AppTestCase, AuthUtils):
    config_file = 'tests.auth'

    su_user = {
        "username": "superman",
        "password": "superman"
    }

    async def test_permissions(self):
        request = await self.client.get('/objectives')
        data = self.json(request.response, 200)
        self.assertTrue(data['result'])
