import lux
from lux.utils import test


class TestCase(test.TestCase):
    config_file = 'tests.auth_ext'

    def test_app(self):
        from pulsar.apps.greenio import WsgiGreen
        app = self.application()
        handle = app.handler
        self.assertIsInstance(handle, WsgiGreen)
        self.assertEqual(handle.pool, None)
        mapper = app.mapper()
        self.assertEqual(len(mapper), 4)

    def test_command_create_superuser(self):
        app = self.application()
        yield from self.run_command(app, 'create_databases')
        yield from self.run_command(app, 'create_tables')
        yield from self.run_command(app, 'create_superuser',
                                    interactive=False, username='pippo',
                                    password='pluto')
        user = yield from app.mapper().user.get(username='pippo')
        self.assertEqual(user.username, 'pippo')
        self.assertTrue(user.is_active())
        self.assertTrue(user.is_superuser())

    def __test_create_user(self):
        app = self.application()
        permissions = app.permissions
        self.assertEqual(len(permissions.auth_backends), 1)
        user = yield from permissions.create_superuser(app.wsgi_request(),
                                                       username='luxtest',
                                                       password='plain')
        self.assertEqual(user.username, 'luxtest')
        self.assertTrue(user.is_superuser)
