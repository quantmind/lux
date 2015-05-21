from lux.utils import test


class AdminTest(test.AppTestCase):
    config_file = 'tests.mail'

    def test_backend(self):
        from lux.extensions.smtp import EmailBackend
        backend = self.app.email_backend
        self.assertIsInstance(backend, EmailBackend)

    def test_send_mail(self):
        backend = self.app.email_backend
        sent = yield from backend.send_mail(to='pippo@foo.com',
                                            subject='Hello!',
                                            message='This is a test message')
        self.assertEqual(sent, 0)
