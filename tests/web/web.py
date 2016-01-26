__test__ = False

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.admin',
              'lux.extensions.auth']

API_URL = ''
AUTHENTICATION_BACKENDS = ['bmllportal.auth.ApiSessionBackend',
                           'lux.extensions.rest.backends.CsrfBackend']
