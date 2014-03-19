import lux
from lux.utils import test


class TestCase(test.TestCase):
    config_params = {'EXTENSIONS': ['lux.extensions.api',
                                    'lux.extensions.sessions']}

    def test_create_superuser(self):
        command = self.fetch_command('create_superuser')
        result = yield command((), interactive=False)
        self.assertEqual(result, None)

    def test_create_user(self):
        app = self.application()
        permissions = app.permissions
        self.assertEqual(len(permissions.auth_backends), 1)
        user = yield permissions.create_superuser(app.wsgi_request(),
                                                  username='luxtest',
                                                  password='plain')
        self.assertEqual(user.username, 'luxtest')
        self.assertTrue(user.is_superuser)
