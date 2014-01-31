import io

from lux.utils import test


class CommandTests(test.TestCase):
    config_params = {'EXTENSIONS': ['lux.extensions.deploy']}

    def test_nginx(self):
        command = self.fetch_command('nginx')
        stream = io.StringIO()
        command((), target=stream)
