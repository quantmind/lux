from lux.utils import test

from . import postgresql


class TestSqlite(postgresql.TestPostgreSql):
    config_params = {'DATASTORE': 'sqlite://'}
