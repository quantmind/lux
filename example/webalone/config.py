from example.cfg import *   # noqa

EXTENSIONS = EXTENSIONS + (
    'lux.extensions.angular',
    'lux.extensions.auth',
    'lux.extensions.odm',
)

DEFAULT_CONTENT_TYPE = 'text/html'
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.SessionBackend',
                           'lux.extensions.rest.backends.CsrfBackend',
                           'lux.extensions.rest.backends.BrowserBackend']
