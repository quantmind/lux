from lux.core import LuxExtension

EXTENSIONS = ['lux.extensions.smtp']

EMAIL_USE_TLS = True
EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'server@luxtest.com'
EMAIL_HOST_PASSWORD = 'dummy'
DEFAULT_FROM_EMAIL = 'admin@luxtest.com'
SMTP_LOG_LEVEL = 'ERROR'


class Extension(LuxExtension):
    pass
