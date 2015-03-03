"""
lux/pulsar settings for $project_name project.
"""

SECRET_KEY = '$secret_key'
SESSION_COOKIE_NAME = '$project_name'

AUTHENTICATION_BACKEND = 'lux.extensions.auth.models.SessionBackend'


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.ui',
              'lux.extensions.cms',
              'lux.extensions.auth']
