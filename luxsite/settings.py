"""
lux/pulsar settings for luxsite project.
"""
APP_NAME = 'Lux'
HTML_TITLE = 'Lux - web toolkit for python and angularJS'
SITE_URL = 'http://quantmind.github.io/lux'
EXTENSIONS = ('lux.extensions.base',
              'lux.extensions.ui',
              'lux.extensions.angular',
              'lux.extensions.static')

CONTEXT_LOCATION = 'luxsite/contents/context'
STATIC_LOCATION = '../docs/luxsite'
MD_EXTENSIONS = ['extra', 'meta', 'toc']

REQUIREJS = ['lux']
FAVICON = 'luxsite/favicon.ico'
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
              'luxsite/luxsite.css')

SECRET_KEY = '(_qja2=t^orv+_o^3cq$0l#-%yvq*xitp66$^e-cm7c2ir8+&!'
