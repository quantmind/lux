from . import postgresql


class TestCMSsqlite(postgresql.TestCMSpostgresql):
    config_params = {'DATASTORE': 'sqlite://'}
