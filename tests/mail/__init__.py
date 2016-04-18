from lux.core import LuxExtension
from lux.extensions.smtp import ContactRouter

EXTENSIONS = ['lux.extensions.smtp']

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


class Extension(LuxExtension):

    def middleware(self, app):
        return [ContactRouter('contact')]
