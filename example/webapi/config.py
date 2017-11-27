from example.cfg import *   # noqa


API_URL = ''
AUTHENTICATION_BACKENDS = ['lux.ext.auth:TokenBackend']
DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'
SERVE_STATIC_FILES = False
