from tests.web.cfg import *   # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.auth']

API_URL = ''
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']
DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'
