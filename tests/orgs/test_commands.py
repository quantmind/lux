from tests import orgs


class TestCommand(orgs.AppTestCase):

    async def test_new_app_token(self):
        result = await self.client.run_command('new_app_token')
        self.assertEqual(len(result), 64)
