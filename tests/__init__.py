import os

from lux.utils import test


fixtures = os.path.join(os.path.dirname(__file__), 'auth', 'fixtures')


class AuthFixtureMixin:

    @classmethod
    def populatedb(cls):
        test.load_fixtures(cls.app, fixtures)
