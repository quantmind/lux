from inspect import ismethod

from lux.utils import test
from lux.extensions import api


class DummyManager:
    model = None


class CrudTests(test.TestCase):
    config_file = 'luxpy.api'

    def test_crud(self):
        router = api.CRUD('bla', manager=DummyManager())
        self.assertEqual(router.route.path, '/bla')
        self.assertEqual(len(router.routes), 2)
        r1 = router.routes[0]
        # This router should have both get and put method
        get = getattr(r1, 'get', None)
        self.assertTrue(ismethod(get))

    def test_create_tables_command(self):
        cmnd = self.fetch_command('create_tables')
