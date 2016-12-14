import os

from lux.core import CommandError

from tests import content


class TestStaticSite(content.Test):

    async def test_static(self):
        command = self.app.get_command('static')
        self.assertTrue(command.help)

        with self.assertRaises(CommandError) as r:
            await command(['--static-path', content.CONTENT_REPO])
        self.assertEqual(str(r.exception),
                         'specify base url with --base-url flag')

        await command(['--static-path', content.CONTENT_REPO,
                       '--base-url', 'http://bla.com'])
        index = os.path.join(content.CONTENT_REPO, 'index.html')
        self.assertTrue(os.path.isfile(index))
