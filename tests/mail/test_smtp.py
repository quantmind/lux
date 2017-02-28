from lux.utils import test
from lux.extensions.smtp import EmailBackend


class SmtpTest(test.AppTestCase):
    config_file = 'tests.mail'

    @classmethod
    def beforeAll(cls):
        email = cls.app.email_backend
        email.send_mails = email._send_mails

    def test_backend(self):
        backend = self.app.email_backend
        self.assertIsInstance(backend, EmailBackend)

    def test_send_mail(self):
        backend = self.app.email_backend
        sent = backend.send_mail(to='pippo@foo.com',
                                 subject='Hello!',
                                 message='This is a test message')
        self.assertEqual(sent, 1)

    def test_send_html_mail(self):
        backend = self.app.email_backend
        sent = backend.send_mail(to='pippo@foo.com',
                                 subject='Hello!',
                                 html_message='<p>This is a test</p>')
        self.assertEqual(sent, 1)
        message, _ = backend.sent.pop()
        body = message[2].decode('utf-8')
        self.assertEqual(message[1][0], 'pippo@foo.com')
        self.assertTrue('<p>This is a test</p>' in body)
