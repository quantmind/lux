from unittest import skipUnless

try:
    from redis import StrictRedis
except ImportError:
    StrictRedis = None

from pulsar import ImproperlyConfigured
from pulsar.apps.test import check_server
from pulsar.apps.data.redis.client import RedisClient

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
                          lambda: app.cache_server)


@skipUnless(REDIS_OK, 'Requires a running Redis server')
class TestRedisCache(test.AppTestCase):
    config_params = {'GREEN_POOL': 20}
    ClientClass = RedisClient

    @classmethod
    def setUpClass(cls):
        redis = 'redis://%s' % cls.cfg.redis_server
        cls.config_params.update({'CACHE_SERVER': redis})
        return super().setUpClass()

    def test_client(self):
        cache = self.app.cache_server
        self.assertTrue(cache.client, self.ClientClass)

    @test.green
    def test_redis_cache(self):
        cache = self.app.cache_server
        self.assertEqual(cache.name, 'redis')
        key = test.randomname()
        self.assertEqual(cache.get_json(key), None)
        data = {'name': 'pippo', 'age': 4}
        self.assertEqual(cache.set_json(key, data), None)
        self.assertEqual(cache.get_json(key), data)

    @test.green
    def test_get_json(self):
        cache = self.app.cache_server
        self.assertEqual(cache.name, 'redis')
        key = test.randomname()
        self.assertEqual(cache.set(key, '{bad-json}'), None)
        self.assertEqual(cache.get_json(key), None)
        self.assertEqual(cache.get(key), b'{bad-json}')


@skipUnless(REDIS_OK and StrictRedis, ('Requires a running Redis server and '
                                       'redis python client'))
class TestRedisCacheSync(TestRedisCache):
    config_params = {}
    ClientClass = StrictRedis
