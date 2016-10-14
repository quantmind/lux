from lux.core import LuxExtension
from lux.extensions import smtp

EXTENSIONS = ['lux.extensions.smtp']

DEFAULT_CONTENT_TYPE = 'text/html'
EMAIL_BACKEND = 'tests.mail.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'server@luxtest.com'
EMAIL_HOST_PASSWORD = 'dummy'
EMAIL_DEFAULT_FROM = 'admin@luxtest.com'
EMAIL_DEFAULT_TO = 'info@luxtest.com'
SMTP_LOG_LEVEL = 'ERROR'

EMAIL_ENQUIRY_RESPONSE = [
    {
        "subject": "Website enquiry from: {{ name }} <{{ email }}>",
        "message": "{{ body }}"
    },
    {
        "to": "{{ email }}",
        "subject": "Thank you for your enquiry",
        "message-template": "enquiry-response.txt"
    }
]


class EmailBackend(smtp.EmailBackend):

    def __init__(self, app):
        self.app = app
        self.sent = []

    async def send_mails(self, messages):
        return self._send_mails(messages)

    def _open(self):
        return DummyConnection(self)


class Extension(LuxExtension):
    pass


class DummyConnection:

    def __init__(self, backend):
        self.backend = backend

    def sendmail(self, *args, **kwargs):
        self.backend.sent.append((args, kwargs))

    def quit(self):
        pass
