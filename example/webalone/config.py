from example.cfg import *   # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.auth']

DEFAULT_CONTENT_TYPE = 'text/html'
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.SessionBackend',
                           'lux.extensions.rest.backends.CsrfBackend',
                           'lux.extensions.rest.backends.BrowserBackend']
