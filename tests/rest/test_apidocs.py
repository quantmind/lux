import os

from lux.utils import test


class TestDictModel(test.TestCase):
    config_file = 'tests.rest'
    config_params = dict(
        API_URL='/',
        EXTENSIONS=[
            'lux.ext.rest',
            'lux.ext.odm',
            'lux.ext.auth',
            'lux.ext.apps',
            'lux.ext.orgs'
        ]
    )

    async def test_api_doc(self):
        command = self.fetch_command('openapi_docs')
        self.assertTrue(command.help)
        files = await command([])
        self.assertTrue(files)
        for filename in files:
            os.remove(filename)
