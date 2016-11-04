from lux.core import CommandError
from lux.utils import test


class OrganisationTest(test.TestCase):
    config_file = 'tests.orgs.config'

    async def test_command_error(self):
        app = self.application(MASTER_APPLICATION_ID=None)
        client = test.TestClient(app)
        await self.wait.assertRaises(
            CommandError, client.run_command, 'admin_app'
        )
