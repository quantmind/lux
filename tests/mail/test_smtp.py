from lux.utils import test


class SmtpTest(test.AppTestCase):
    config_file = 'tests.mail'

    def test_backend(self):
        from lux.extensions.smtp import EmailBackend
        backend = self.app.email_backend
        self.assertIsInstance(backend, EmailBackend)

    async def test_send_mail_fail(self):
        backend = self.app.email_backend
        sent = await backend.send_mail(to='pippo@foo.com',
                                       subject='Hello!',
                                       message='This is a test message')
        self.assertEqual(sent, 0)


class SmtpMockTest(test.AppTestCase):
    config_file = 'tests.mail'

    @classmethod
    def beforeAll(cls):
        backend = cls.app.email_backend
        backend._open = cls._backend_open

    async def test_send_mail_fail(self):
        backend = self.app.email_backend
        sent = await backend.send_mail(to='pippo@foo.com',
                                       subject='Hello!',
                                       message='This is a test message')
        self.assertEqual(sent, 1)

    @classmethod
    def _backend_open(cls):
        return DummyConnection(cls.app)


class DummyConnection:

    def __init__(self, app):
        self.app = app
        self.sent = []

    def sendmail(self, *args, **kwargs):
        self.sent.append((args, kwargs))

    def quit(self):
        pass
