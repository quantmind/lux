from example.cfg import *   # noqa

API_URL = 'api'
DEFAULT_CONTENT_TYPE = 'text/html'
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.SessionBackend',
                           'lux.extensions.rest.backends.CsrfBackend',
                           'lux.extensions.rest.backends.BrowserBackend']

HTML_SCRIPTS = ['website/website']
