from tests.web.cfg import *   # noqa

APP_NAME = COPYRIGHT = HTML_TITLE = 'website.com'
SESSION_COOKIE_NAME = 'test-website'
EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.content',
              'lux.extensions.admin',
              'tests.web.content']

API_URL = 'http://webapi.com'
AUTHENTICATION_BACKENDS = ['lux.extensions.rest.backends.ApiSessionBackend',
                           'lux.extensions.rest.backends.CsrfBackend']

SERVE_STATIC_FILES = True
CLEAN_URL = True
REDIRECTS = {'/tos': '/articles/terms-conditions'}
