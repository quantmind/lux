"""Organisation and user permissions"""
from lux.utils import test


class OrganisationTest(test.AppTestCase):
    config_file = 'tests.orgs.config'

    @classmethod
    def create_admin_jwt(cls):
        return cls.client.run_command('admin_app')

    @classmethod
    async def beforeAll(cls):
        request = await cls.client.post(
            cls.api_url('authorizations'),
            json=dict(username='testuser', password='testuser'),
            jwt=cls.admin_jwt
        )
        cls.super_token = cls._test.json(request.response, 201)['id']

    @test.green
    def _test_entity(self, username, type):
        odm = self.app.odm()
        with odm.begin() as session:
            entity = session.query(odm.entity).filter_by(username=username)
            self.assertEqual(entity.one().type, type)

    async def test_create_organisation(self):
        username = 'testorg'
        body = {
            'username': username,
            'billing_email_address': 'asdfasdf@asdfasdf.com'
        }
        request = await self.client.post(self.api_url('organisations'),
                                         json=body,
                                         token=self.super_token)
        org = self.json(request.response, 201)
        await self._test_entity(org['username'], 'organisation')
        request = await self.client.get(
            self.api_url('organisations/testorg/members'),
            token=self.super_token
        )
        members = self.json(request.response, 200)
        self.assertEqual(len(members['result']), 1)
        member = members['result'][0]
        self.assertFalse('superuser' in member)
        self.assertFalse('active' in member)
        self.assertEqual(member['role'], 'owner')

    async def test_list_organisation(self):
        request = await self.client.get(
            self.api_url('organisations'),
            token=self.super_token
        )
        data = self.json(request.response, 200)['result']
        self.assertTrue(data)

    async def test_organisation_members(self):
        request = await self.client.get(
            self.api_url('organisations/org1/members'))
        orgs = self.json(request.response, 200)['result']
        self.assertGreaterEqual(len(orgs), 1)
        member = orgs[0]
        self.assertEqual(member['username'], 'pippo')
        self.assertEqual(member['role'], 'owner')

    async def test_organisation_member_404(self):
        request = await self.client.get(
            self.api_url('organisations/org1/members/foo'))
        self.json(request.response, 404)

    async def test_organisation_member(self):
        request = await self.client.get(
            self.api_url('organisations/org1/members/pippo'))
        member = self.json(request.response, 200)
        self.assertEqual(member['username'], 'pippo')
        self.assertEqual(member['role'], 'owner')
        self.assertEqual(member['organisation'], 'org1')
        request = await self.client.get(
            self.api_url('organisations/org2/members/pluto'))
        member = self.json(request.response, 200)
        self.assertEqual(member['username'], 'pluto')
        self.assertEqual(member['role'], 'owner')
        self.assertEqual(member['organisation'], 'org2')

    async def test_organisation_delete_member_fail(self):
        request = await self.client.delete(
            self.api_url('organisations/org1/members/pippo')
        )
        self.json(request.response, 401)
        token = await self.user_token('pluto', jwt=self.admin_jwt)
        request = await self.client.delete(
            self.api_url('organisations/org1/members/pippo'),
            token=token
        )
        self.json(request.response, 403)

    async def test_organisation_delete_member_fail_owner(self):
        token = await self.user_token('pippo', jwt=self.admin_jwt)
        request = await self.client.delete(
            self.api_url('organisations/org1/members/pippo'),
            token=token
        )
        data = self.json(request.response, 403)
        self.assertEqual(data['message'],
                         'Cannot remove owner - only one available')

    async def test_organisation_add_member(self):
        token = await self.user_token('pippo', jwt=self.admin_jwt)
        request = await self.client.post(
            self.api_url('organisations'),
            token=token,
            json=dict(
                username='org876',
                billing_email_address='info@org876.com'
            )
        )
        self.json(request.response, 201)
        request = await self.client.post(
            self.api_url('organisations/org876/members/pluto'),
            json=dict(role='member')
        )
        data = self.json(request.response, 200)
        self.assertEqual(data['role'], 'member')
        request = await self.client.get(
            self.api_url('organisations/org876/members')
        )
        data = self.json(request.response, 200)['result']
        self.assertEqual(len(data), 2)

    async def __test_user_organisations(self):
        token = await self.user_token('pippo', jwt=self.admin_jwt)
        request = await self.client.get(self.api_url('user'),
                                        token=token)
        self.json(request.response, 200)
        request = await self.client.get(self.api_url('user/organisations'),
                                        token=token)
        orgs = self.json(request.response, 200)['result']
        self.assertGreaterEqual(len(orgs), 1)
