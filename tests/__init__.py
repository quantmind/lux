import os

from lux.utils import test


fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')


class AuthFixtureMixin:

    @classmethod
    def populatedb(cls):
        return test.load_fixtures(cls.app, fixtures)
