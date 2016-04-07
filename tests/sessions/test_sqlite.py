import tests.sessions.test_postgresql as postgresql


class TestSqlite(postgresql.TestPostgreSql):
    config_params = {'DATASTORE': 'sqlite://'}
