from example.cfg import *   # noqa

APP_NAME = COPYRIGHT = HTML_TITLE = 'website.com'

EXTENSIONS = ('lux.extensions.base',
              'lux.extensions.angular',
              'lux.extensions.rest',
              'lux.extensions.ui',
              'lux.extensions.content')

DEFAULT_CONTENT_TYPE = 'text/html'
API_URL = 'http://webapi.com'
AUTHENTICATION_BACKENDS = ['lux.extensions.rest.backends.ApiSessionBackend',
                           'lux.extensions.rest.backends.CsrfBackend']

SERVE_STATIC_FILES = True
CLEAN_URL = True
REDIRECTS = {'/tos': '/articles/terms-conditions'}


HTML_LINKS = ({'href': 'luxsite/lux-114.png',
               'sizes': '57x57',
               'rel': 'apple-touch-icon'},
              {'href': 'luxsite/lux-114.png',
               'sizes': '114x114',
               'rel': 'apple-touch-icon'},
              {'href': 'luxsite/lux-144.png',
               'sizes': '72x72',
               'rel': 'apple-touch-icon'},
              {'href': 'luxsite/lux-144.png',
               'sizes': '144x144',
               'rel': 'apple-touch-icon'},
              'luxsite/luxsite')
