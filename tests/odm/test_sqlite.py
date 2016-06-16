import tests.odm.test_postgresql as postgresql

from tests.odm.utils import SqliteMixin


class TestSql(SqliteMixin, postgresql.TestPostgreSql):
    pass
