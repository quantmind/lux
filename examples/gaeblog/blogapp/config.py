from lux.extensions.gae import isdev
from lux.extensions.ui import CssLibraries

from .routes import handleError

SECRET_KEY = '=!82m0!!e=7u3tfrp=hpt2x@2b(xawgna$us!mswf9a+jzzrqn'

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.sessions',
              'lux.extensions.ui',
              'lux.extensions.api',
              'lux.extensions.angular',
              'lux.extensions.code',
              'blog']

APP_NAME = 'Lux Blog'
APP_ID = 'luxgaeblog'
SITE_URL = 'https://luxgaeblog.appspot.com'
ADMIN_EMAIL = 'info@quantmind.com'
TIME_FORMAT_STRING = '%b %d, %Y %I:%M:%S %p'
HTML_TITLE = 'Lux blog - a blog for created using Lux'
COMPANY = 'Quantmind'
DEFAULT_FROM_EMAIL = 'info@quantmind.com'
MEDIA_URL = '/media/'
MINIFIED_MEDIA = True
CLEAN_URL = True
FAVICON = 'blogapp/favicon.ico'
HTML_META = [{'http-equiv': 'X-UA-Compatible',
              'content': 'IE=edge'},
             {'name': 'viewport',
              'content': 'width=device-width, initial-scale=1'},
             {'name': 'description',
              'content': "A blog site by quantmind"}]
HTML_LINKS = [CssLibraries['katex'], 'blogapp/blogapp.css']
REQUIREJS = ['blogapp/blogapp']
REQUIREJS_CONFIG = MEDIA_URL + 'blogapp/require.config.min.js'
SESSION_COOKIE_NAME = APP_ID
AUTHENTICATION_BACKEND = 'blogapp.MultiAuthBackend'
ANGULAR_UI_ROUTER = True
ANGULAR_VIEW_ANIMATE = 'animate-fade'

ERROR_HANDLER = handleError

# DEVELOPMENT MODE
if isdev():
    SITE_URL = ''
    MINIFIED_MEDIA = False
