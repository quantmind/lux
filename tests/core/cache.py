from unittest import skipUnless

from pulsar import ImproperlyConfigured
from pulsar.apps.test import check_server

from lux.utils import test


REDIS_OK = check_server('redis')


class TestWrappers(test.TestCase):

    def test_dummy_cache(self):
        app = self.application()
        cache = app.cache_server
        from lux.core.cache import Cache
        self.assertIsInstance(cache, Cache)
        self.assertEqual(cache.ping(), True)
        self.assertEqual(cache.hmget('bla'), None)
        cache.hmset('foo', {'name': 'pippo'})
        self.assertEqual(cache.hmget('foo'), None)
        cache.set('h', 56)
        self.assertEqual(cache.get('h'), None)

    def test_bad_url(self):
        app = self.application(CACHE_SERVER='cbjhb://')
        self.assertRaises(ImproperlyConfigured,
                          lambda : app.cache_server)


@skipUnless(REDIS_OK, 'Requires a running Redis server')
class TestRedisCache(test.AppTestCase):
    config_params = {'CACHE_SERVER': 'sqlite://'}

    @classmethod
    def setUpClass(cls):
        redis = 'redis://%s' % cls.cfg.redis_server
        cls.config_params = {'CACHE_SERVER': redis,
                             'GREEN_POOL': 20}
        return super().setUpClass()

    @test.green
    def test_redis_cache(self):
        cache = self.app.cache_server
        self.assertEqual(cache.name, 'redis')
        key = test.randomname()
        self.assertEqual(cache.get_json(key), None)
        data = {'name': 'pippo', 'age': 4}
        self.assertEqual(cache.set_json(key, data), None)
        self.assertEqual(cache.get_json(key), data)
