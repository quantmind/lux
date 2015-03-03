"""
lux/pulsar settings for $project_name project.
"""
HTML_TITLE = '$project_name'
DESCRIPTION = ('$project_name')

SECRET_KEY = '$secret_key'
SESSION_COOKIE_NAME = '$project_name'

AUTHENTICATION_BACKEND = 'lux.extensions.auth.models.SessionBackend'


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.ui',
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

HTML_TEMPLATES = {'/': 'home.html',
                  LOGIN_URL: 'small.html'}

# PULSAR config
loglevel = ['pulsar.info']
