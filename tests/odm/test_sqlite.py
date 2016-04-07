from lux.utils import test

import tests.odm.test_postgresql as postgresql


class TestSqliteMixin:
    config_params = {'DATASTORE': 'sqlite://'}


@test.sequential
class TestSql(TestSqliteMixin, postgresql.TestPostgreSql):
    pass
