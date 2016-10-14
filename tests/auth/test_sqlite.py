import tests.auth.test_postgresql as test


class TestSqlite(test.TestPostgreSql):
    config_params = {'DATASTORE': 'sqlite://'}
