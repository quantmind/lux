from . import sqlite


class TestRethinkDB(sqlite.TestSqlite):
    config_params = {'DATASTORE': 'rethinkdb://127.0.0.1:28015/luxtests',
                     'GREEN_POOL': 50}

