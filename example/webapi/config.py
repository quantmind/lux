from example.cfg import *   # noqa

EXTENSIONS = EXTENSIONS + (
    'lux.extensions.auth',
    'lux.extensions.odm'
)

API_URL = ''
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']
DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'

DEFAULT_PERMISSION_LEVEL = 'none'
DEFAULT_PERMISSION_LEVELS = {'user': 'read',
                             'site': 'read',
                             'articles': 'read'}
