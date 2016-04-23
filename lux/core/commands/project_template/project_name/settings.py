"""
$project_name settings
"""
APP_NAME = '$project_name'
HTML_TITLE = '$project_name'
DESCRIPTION = '$project_name'

SECRET_KEY = '$secret_key'
SESSION_COOKIE_NAME = APP_NAME.lower()

AUTHENTICATION_BACKENDS = ['lux.extensions.auth.SessionBackend',
                           'lux.extensions.rest.backends.CsrfBackend',
                           'lux.extensions.rest.backends.BrowserBackend']


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.cms',
              'lux.extensions.auth']

HTML_META = [{'http-equiv': 'X-UA-Compatible',
              'content': 'IE=edge'},
             {'name': 'viewport',
              'content': 'width=device-width, initial-scale=1'},
             {'name': 'description', 'content': DESCRIPTION}]

SERVE_STATIC_FILES = True
REQUIREJS = ('$project_name/$project_name',)
FAVICON = '$project_name/favicon.ico'
HTML_LINKS = ['$project_name/$project_name']

LOGIN_URL = '/login'
REGISTER_URL = '/signup'
RESET_PASSWORD_URL = '/reset-password'

HTML_TEMPLATES = {'/': 'home.html',
                  LOGIN_URL: 'small.html',
                  REGISTER_URL: 'small.html',
                  RESET_PASSWORD_URL: 'small.html'}

# PULSAR config
log_level = ['pulsar.info']
