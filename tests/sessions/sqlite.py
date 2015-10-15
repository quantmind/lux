from . import postgresql


class TestSqlite(postgresql.TestPostgreSql):
    config_params = {'DATASTORE': 'sqlite://'}
