from lux.utils import test

from . import postgresql


class TestSql(postgresql.TestPostgreSql):
    config_params = {'DATASTORE': 'sqlite://'}
