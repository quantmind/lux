from example.cfg import *   # noqa

API_URL = '/api'
DEFAULT_CONTENT_TYPE = 'text/html'
#
# sessions
AUTHENTICATION_BACKENDS = [
    'lux.extensions.sessions:SessionBackend',
    'lux.extensions.auth:TokenBackend'
]
SESSION_EXCLUDE_URLS = [
    'api',
    'api/<path:path>',
    'media',
    'media/<path:path>'
]
#
EXTENSIONS += ('lux.extensions.sessions',)      # noqa
HTML_SCRIPTS = ['website/website']
DEFAULT_POLICY = [
    {
        "resource": "api:contents:*",
        "action": "read"
    }
]
