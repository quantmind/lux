from pulsar.api import Http404

from lux.core import CommandError
from lux.utils import test
from lux.extensions.organisations.ownership import get_owned_model


class OrganisationTest(test.TestCase):
    config_file = 'tests.orgs.config'

    async def test_command_error(self):
        app = self.application(MASTER_APPLICATION_ID=None)
        client = test.TestClient(app)
        await self.wait.assertRaises(
            CommandError, client.run_command, 'admin_app'
        )

    def test_owner_target_404(self):
        app = self.application()
        self.assertRaises(Http404, get_owned_model, app, 'foo')

    def test_owner_target(self):
        app = self.application()
        target = get_owned_model(app, 'projects')
        self.assertTrue(target)
