from lux.utils import test


class TestWrappers(test.TestCase):

    def test_dummy_cache(self):
        app = self.application()
        cache = app.cache_server
        from lux.core.cache import DummyStore
        self.assertIsInstance(cache, DummyStore)
        self.assertEqual(cache.ping(), True)
        self.assertEqual(cache.hmget('bla'), None)
        cache.hmset('foo', {'name': 'pippo'})
        self.assertEqual(cache.hmget('foo'), None)
        cache.set('h', 56)
        self.assertEqual(cache.get('h'), None)
