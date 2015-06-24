from lux.utils import test

from . import postgresql


@test.sequential
class TestSql(postgresql.TestPostgreSql):
    config_params = {'DATASTORE': 'sqlite://'}
