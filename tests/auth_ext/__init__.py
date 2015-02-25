from tests.config import *

EXTENSIONS = ['lux.extensions.auth',
              'lux.extensions.api',
              'lux.extensions.odm']

AUTHENTICATION_BACKEND = 'lux.extensions.auth.models.SessionBackend'
