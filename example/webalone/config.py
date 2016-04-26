from example.cfg import *   # noqa

EXTENSIONS = EXTENSIONS + (
    'lux.extensions.angular',
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

SERVE_STATIC_FILES = True
HTML_SCRIPTS = ['website/website']
