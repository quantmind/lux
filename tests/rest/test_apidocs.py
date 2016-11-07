import os

from lux.utils import test


class TestDictModel(test.TestCase):
    config_file = 'tests.rest'
    config_params = dict(
        API_URL='/',
        EXTENSIONS=[
            'lux.extensions.rest',
            'lux.extensions.odm',
            'lux.extensions.auth',
            'lux.extensions.applications',
            'lux.extensions.organisations'
        ]
    )

    async def test_api_doc(self):
        command = self.fetch_command('openapi_docs')
        self.assertTrue(command.help)
        files = await command([])
        self.assertTrue(files)
        for filename in files:
            os.remove(filename)
