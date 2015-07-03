import json

from dateutil.parser import parse

from lux.utils import test

from . import postgresql


class TestCMSsqlite(postgresql.TestCMSpostgresql):
    config_params = {'DATASTORE': 'sqlite://'}
