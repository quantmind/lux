"""Organisation & User ownership of models"""
from tests import orgs


class OrganisationTest(orgs.AppTestCase):

    async def test_create_user_project(self):
        request = await self.client.post(
            self.api_url('user/projects'),
            json=dict(name="project1", private=True),
            token=self.super_token
        )
        data = self.json(request.response, 201)
        self.assertEqual(data['name'], 'project1')
        self.assertTrue(data['id'])
        #
        # this should fail
        request = await self.client.post(
            self.api_url('user/projects'),
            json=dict(name="project1", private=True),
            token=self.super_token
        )
        self.assertValidationError(request.response, 'name',
                                   'project1 not available')
