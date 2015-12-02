from lux.utils import test

from . import postgresql


class TestSqliteMixin:
    config_params = {'DATASTORE': 'sqlite://'}


@test.sequential
class TestSql(TestSqliteMixin, postgresql.TestPostgreSql):
    pass
