from example.cfg import *   # noqa

EXTENSIONS += ('lux.extensions.sessions',)      # noqa
DEFAULT_CONTENT_TYPE = 'text/html'
API_URL = 'http://webapi.com'
AUTHENTICATION_BACKENDS = [
    'lux.extensions.sessions:SessionBackend'
]

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
