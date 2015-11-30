"""
lux/pulsar settings for $project_name project.
"""
from importlib import import_module

from pulsar.utils.slugify import slugify

import lux


mod = import_module('$project_name')
APP_NAME = '$project_name'
COPYRIGHT = '$project_name'
SECRET_KEY = '$secret_key'
SESSION_COOKIE_NAME = '$project_name'

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.ui',
              'lux.extensions.code',
              'lux.extensions.rest',
              'lux.extensions.admin',
              'lux.extensions.angular',
              'lux.extensions.sitemap']

#
#  For HTML serving applications
SERVE_STATIC_FILES = True
HTML_TITLE = '$project_name'
SCRIPTS = ['$project_name/$project_name']
HTML_LINKS = [
    '//cdnjs.cloudflare.com/ajax/libs/font-awesome/4.4.0/css/font-awesome',
    '//cdnjs.cloudflare.com/ajax/libs/angular-ui-grid/3.0.7/ui-grid',
    '$project_name/$project_name'
]
HTML_META = [{'http-equiv': 'X-UA-Compatible',
              'content': 'IE=edge'},
             {'name': 'viewport',
              'content': 'width=device-width, initial-scale=1'}]
LOGIN_URL = '/login'
REGISTER_URL = '/signup'
RESET_PASSWORD_URL = '/reset-password'
ADMIN_URL = '/admin'
media_version = slugify('%s-%s' % (mod.__version__, lux.__version__))
MEDIA_URL = '/media/%s/' % media_version

HTML_TEMPLATES = {LOGIN_URL: 'small.html',
                  REGISTER_URL: 'small.html',
                  RESET_PASSWORD_URL: 'small.html',
                  '%s/<auth_key>' % RESET_PASSWORD_URL: 'small.html',
                  # Admin
                  ADMIN_URL: 'admin.html',
                  '%s/<path:path>' % ADMIN_URL: 'admin.html'}
