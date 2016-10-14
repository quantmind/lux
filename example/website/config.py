from example.cfg import *   # noqa


DEFAULT_CONTENT_TYPE = 'text/html'
API_URL = 'http://webapi.com'
AUTHENTICATION_BACKENDS = ['lux.extensions.rest.backends.ApiSessionBackend',
                           'lux.extensions.rest.backends.CsrfBackend']

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
