DESCRIPTION = 'Welcome to the test website for lux!'
HTML_TITLE = 'Lux'
EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.ui',
              'lux.extensions.ui.style.all',
              'lux.extensions.sessions',
              'lux.extensions.sitemap',
              'lux.extensions.api',
              'lux.extensions.cms',
              'lux.extensions.services',
              'lux.extensions.debug',
              'jstest']

CLEAN_URL = False
SERVE_STATIC_FILES = True
MINIFIED_JS = False
MEDIA_URL = 'assets'
FAVICON = 'luxweb/favicon.ico'
CSS = {'all': ['luxweb/luxweb.css']}

NAVIGATION_BRAND = "Lux Web"
ADMIN_URL = 'admin'
