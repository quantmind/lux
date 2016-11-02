API_URL = '/'

EXTENSIONS = [
    'lux.extensions.base',
    'lux.extensions.rest',
    'lux.extensions.odm',
    'lux.extensions.auth',
    'lux.extensions.applications',
    'lux.extensions.organisations'
]

ADMIN_APPLICATION_ID = 'cb1dc2bac69d47a1965f4c2c6fc43163'

DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'
