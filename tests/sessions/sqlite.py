from lux.utils import test

from . import postgresql


@test.sequential
class TestSqlite(postgresql.TestPostgreSql):
    config_params = {'DATASTORE': 'sqlite://'}
