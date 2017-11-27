from unittest import skipUnless

try:
    from redis import StrictRedis
except ImportError:     # pragma    nocover
    StrictRedis = None

from pulsar.api import ImproperlyConfigured
from pulsar.apps.test import check_server
from pulsar.utils.string import random_string
from pulsar.apps.data.redis.client import RedisClient

from lux.utils import test

from tests.config import redis_cache_server


REDIS_OK = check_server('redis')


class LockTests:

    @test.green
    def test_lock(self):
        key1 = random_string()
        key2 = random_string()
        lock = self.cache.lock(key1, blocking=False)
        other_lock = self.cache.lock(key2, blocking=False)
        self.assertTrue(lock.acquire())
        self.assertFalse(lock.acquire())
        self.assertTrue(other_lock.acquire())
        other_lock.release()
        lock.release()

    @test.green
    def test_lock_contextmanager(self):
        lock = self.cache.lock('test3', blocking=0.1)
        with lock:
            with self.assertRaises(TimeoutError):
                with lock:
                    pass
        self.assertTrue(lock.acquire())
        lock.release()

    @test.green
    def test_lock_timeout(self):
        lock = self.cache.lock('test4', timeout=0.1, blocking=0.2)
        self.assertTrue(lock.acquire())
        self.assertTrue(lock.acquire())
        lock.release()


class TestDummyCache(test.TestCase, LockTests):

    def setUp(self):
        self.app = self.application()
        self.cache = self.app.cache_server

    def test_dummy_cache(self):
        from lux.core.cache import Cache
        self.assertIsInstance(self.cache, Cache)
        self.assertEqual(self.cache.ping(), True)
        self.assertEqual(self.cache.hmget('bla'), None)
        self.cache.hmset('foo', {'name': 'pippo'})
        self.assertEqual(self.cache.hmget('foo'), None)
        self.cache.set('h', 56)
        self.assertEqual(self.cache.get('h'), None)

    def test_cache_name(self):
        self.assertEqual(self.cache.name, 'dummy')
        self.assertEqual(str(self.cache), 'dummy://')

    def test_bad_url(self):
        app = self.application(CACHE_SERVER='cbjhb://')
        self.assertRaises(ImproperlyConfigured,
                          lambda: app.cache_server)


@skipUnless(REDIS_OK, 'Requires a running Redis server')
class TestRedisCache(test.AppTestCase, LockTests):
    config_params = {'CACHE_SERVER': redis_cache_server}
    ClientClass = RedisClient

    def setUp(self):
        self.cache = self.app.cache_server

    def test_client(self):
        self.assertTrue(self.cache.client, self.ClientClass)

    @test.green
    def test_redis_cache(self):
        self.assertEqual(self.cache.name, 'redis')
        key = test.randomname()
        self.assertEqual(self.cache.get_json(key), None)
        data = {'name': 'pippo', 'age': 4}
        self.assertEqual(self.cache.set_json(key, data), None)
        self.assertEqual(self.cache.get_json(key), data)

    @test.green
    def test_get_json(self):
        self.assertEqual(self.cache.name, 'redis')
        key = test.randomname()
        self.assertEqual(self.cache.set(key, '{bad-json}'), None)
        self.assertEqual(self.cache.get_json(key), None)
        self.assertEqual(self.cache.get(key), b'{bad-json}')


@skipUnless(REDIS_OK and StrictRedis, ('Requires a running Redis server and '
                                       'redis python client'))
class TestRedisCacheSync(TestRedisCache):
    ClientClass = StrictRedis
