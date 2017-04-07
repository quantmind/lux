API_URL = '/'

EXTENSIONS = [
    'lux.ext.base',
    'lux.ext.rest',
    'lux.ext.odm',
    'lux.ext.auth',
    'lux.ext.apps',
    'lux.ext.orgs'
]

AUTHENTICATION_BACKENDS = [
    'lux.ext.applications:AuthBackend'
]

MASTER_APPLICATION_ID = 'cb1dc2bac69d47a1965f4c2c6fc43163'

DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'


DEFAULT_POLICY = [
    {
        "resource": [
            "organisations:*"
        ],
        "action": "read"
    }
]
