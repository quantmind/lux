from example.cfg import *   # noqa

EXTENSIONS = EXTENSIONS + (
    'lux.extensions.admin',
    'lux.extensions.auth',
    'lux.extensions.odm',
    'example.website'  # Add this extension for javascript
)

API_URL = 'api'
DEFAULT_CONTENT_TYPE = 'text/html'
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.SessionBackend',
                           'lux.extensions.rest.backends.CsrfBackend',
                           'lux.extensions.rest.backends.BrowserBackend']

HTML_SCRIPTS = ['website/website']
