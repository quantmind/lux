import json

from dateutil.parser import parse

from lux.utils import test

from . import postgresql


@test.sequential
class TestCMSsqlite(postgresql.TestCMSpostgresql):
    config_params = {'DATASTORE': 'sqlite://'}
