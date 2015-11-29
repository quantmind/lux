"""
lux/pulsar settings for $project_name project.
"""
APP_NAME = '$project_name'
SECRET_KEY = '$secret_key'
SESSION_COOKIE_NAME = '$project_name'

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.ui',
              'lux.extensions.code',
              'lux.extensions.rest',
              'lux.extensions.admin',
              'lux.extensions.angular',
              'lux.extensions.sitemap']

SERVE_STATIC_FILES = True
SCRIPTS = ['$project_name/$project_name']
HTML_LINKS = [
    '//cdnjs.cloudflare.com/ajax/libs/font-awesome/4.4.0/css/font-awesome',
    '//cdnjs.cloudflare.com/ajax/libs/angular-ui-grid/3.0.7/ui-grid',
    '$project_name/$project_name'
]
