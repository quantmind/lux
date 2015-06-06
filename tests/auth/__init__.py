import lux


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.auth']


AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']
