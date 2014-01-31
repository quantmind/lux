from inspect import ismethod

from lux.utils import test
from lux.extensions import cms


class DummyManager:
    model = None


class CrudTests(test.TestCase):

    def __test_crud(self):
        router = cms.PageCrud('pages', DummyManager())
        self.assertEqual(router.route.path, '/pages')
        self.assertEqual(len(router.routes), 1)
        r1 = router.routes[0]
        # This router should have both get and put method
        get = getattr(r1, 'get', None)
        self.assertTrue(ismethod(get))
        put = getattr(r1, 'put', None)
        self.assertTrue(ismethod(put))
