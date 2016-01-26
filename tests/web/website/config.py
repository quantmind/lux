from tests.web.cfg import *   # noqa

APP_NAME = COPYRIGHT = HTML_TITLE = 'website.com'
SESSION_COOKIE_NAME = 'test-website'
EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.admin']

API_URL = 'http://webapi.com'
AUTHENTICATION_BACKENDS = ['tests.web.website.ApiSessionBackend',
                           'lux.extensions.rest.backends.CsrfBackend']