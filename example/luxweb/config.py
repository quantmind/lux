from stdnet import odm as ODM

DESCRIPTION = 'Welcome to the test website for lux!'
HTML_HEAD_TITLE = 'Lux'
EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.ui',
              'lux.extensions.sessions',
              'lux.extensions.sitemap',
              'lux.extensions.api',
              'lux.extensions.cms',
              'lux.extensions.services',
              'csstest',
              'jstest',
              'bitcoin']

CLEAN_URL = False
SERVE_STATIC_FILES = True
MINIFIED_JS = False
MEDIA_URL = 'assets'
FAVICON = 'luxweb/favicon.ico'
CSS = {'all': ['luxweb/luxweb.css']}

NAVIGATION_BRAND = "Lux Web"
ADMIN_URL = 'admin'

DATASTORE = {'': 'redis://localhost:6379?db=3&namespace=luxweb:'}
