from . import sqlite


class TestPostgreSql(sqlite.TestSqlite):
    config_params = {
        'DATASTORE': 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests',
        'DEFAULT_PERMISSION_LEVELS': {
            'objective': 40,
            'objective:subject': 0,
            'objective:deadline': 20,
            'objective:outcome': 10
        }
    }
