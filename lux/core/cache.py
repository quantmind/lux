import json
import logging
import asyncio

from copy import copy
from inspect import isfunction

from pulsar.utils.slugify import slugify
from pulsar.apps.data import parse_store_url, create_store
from pulsar.utils.importer import module_attribute
from pulsar.utils.string import to_string
from pulsar import ImproperlyConfigured, Lock

from .component import AppComponent


logger = logging.getLogger('lux.cache')

data_caches = {}


def passthrough(value):
    return value


def cached(*args, **kw):
    """Decorator to apply to Router's methods for
    caching the return value
    """
    if len(args) == 1 and not kw and isfunction(args[0]):
        cache = CacheObject()
        return cache(args[0])
    else:
        return CacheObject(*args, **kw)


class Cache(AppComponent):
    """Cache base class
    """
    def __init__(self, app, name, url):
        super().__init__(app)
        self.name = name
        self.url = url
        self._wait = app.green_pool.wait if app.green_pool else passthrough

    def __repr__(self):
        return self.url
    __str__ = __repr__

    def ping(self):
        return True

    def set(self, key, value, **params):
        pass

    def get(self, key):
        pass

    def delete(self, key):
        """Delete a key from the cache
        """
        pass

    def hmset(self, key, iterable):
        pass

    def hmget(self, key, *fields):
        pass

    def clear(self, prefix=None):
        pass

    def set_json(self, key, value, timeout=None):
        value = json.dumps(value)
        self.set(key, value, timeout=timeout)

    def get_json(self, key):
        value = self.get(key)
        if value is not None:
            try:
                return json.loads(to_string(value))
            except Exception:
                self.app.logger.warning('Could not convert to JSON: %s',
                                        value)

    def lock(self, name, timeout=None):
        raise NotImplementedError


class DummyCache(Cache):
    """A dummy cache to get you started

    Not useful to anything really!
    """
    def __init__(self, app, name, url):
        super().__init__(app, name, url)
        if app.green_pool:
            from pulsar.apps.greenio import wait
            self._wait = wait
        else:
            self._loop = asyncio.get_event_loop()

    def lock(self, name, **kwargs):
        return GreenLock(Lock(name, **kwargs), self._wait)

    def _wait(self, coro):
        return self._loop.run_until_complete(coro)


class GreenLock:

    def __init__(self, lock, wait):
        self._lock = lock
        self._wait = wait

    def __enter__(self):
        if not self.acquire():
            raise TimeoutError()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self):
        return self._wait(self._lock.acquire())

    def release(self):
        return self._wait(self._lock.release())


class RedisCache(Cache):
    """A cache with redis backend
    """
    def __init__(self, app, name, url):
        super().__init__(app, name, url)
        if app.green_pool:
            self._wait = app.green_pool.wait
            self.client = create_store(url).client()
        else:
            import redis
            self.client = redis.StrictRedis.from_url(url)

    def set(self, key, value, timeout=None):
        if timeout is not None:
            timeout = int(1000*timeout)
        self._wait(self.client.set(key, value, px=timeout))

    def get(self, key):
        return self._wait(self.client.get(key))

    def delete(self, key):
        return self._wait(self.client.delete(key))

    def hmset(self, key, iterable, timeout=None):
        self._wait(self.client.hmset(key, iterable, timeout))

    def hmget(self, key, *fields):
        return self._wait(self.client.hmset(key, *fields))

    def clear(self, prefix=None):
        if prefix is None:
            prefix = self.app.config['APP_NAME']
        pattern = '%s*' % prefix
        self.app.logger.warning('Clearing keys matching %s pattern from %s '
                                'cache', pattern, self)
        result = self.client.eval(clear_cache, (), (pattern,))
        return self._wait(result)

    def lock(self, name, **kwargs):
        return GreenLock(self.client.lock(name, **kwargs), self._wait)

    def _wait(self, value):
        return value


class CacheObject:
    """Object which implement cache functionality on callables.

    A callable can be either a method or a function
    """
    instance = None
    callable = None

    def __init__(self, user=False, timeout=None, key=None, app=None):
        self.user = user
        self.timeout = timeout
        self.key = key
        self.app = app

    def cache_key(self, arg):
        key = self.key or ''
        if hasattr(arg, 'environ'):
            if not key:
                key = arg.path
            if self.user:
                key = '%s-%s' % (key, arg.cache.user)

        app = arg.app

        base = self.callable.__name__
        if self.instance:
            base = '%s-%s' % (type(self.instance).__name__, base)

        base = '%s-%s' % (app.config['APP_NAME'], base)
        return slugify('%s-%s' % (base, key) if key else base)

    def __call__(self, *args, **kw):
        if self.callable is None:
            # Initialisation
            assert len(args) == 1 and not kw
            self.callable = args[0]
            return self

        arg = args[0] if args else None

        if not hasattr(arg, 'app'):
            try:
                if self.instance:
                    arg = self.instance.app
                else:
                    raise AttributeError
            except AttributeError:
                arg = self.app
                if not arg:
                    logger.error('Could not obtain application from first '
                                 'parameter nor from bound instance. '
                                 'Cannot use cache.')

        if arg:
            key = self.cache_key(arg)
            result = arg.app.cache_server.get_json(key)
            if result is not None:
                return result

        if self.instance:
            args = (self.instance,) + args

        result = self.callable(*args, **kw)

        if arg:
            timeout = self.timeout
            app = arg.app
            config = app.config

            if timeout in config:
                timeout = config[timeout]
            try:
                int(timeout)
            except Exception:
                timeout = config['CACHE_DEFAULT_TIMEOUT']

            if timeout:
                try:
                    app.cache_server.set_json(key, result, timeout=timeout)
                except TypeError:
                    app.logger.exception(
                        'Could not convert to JSON a value to set in cache')
                except Exception:
                    app.logger.exception('Critical error while setting cache')

        return result

    def __get__(self, instance, objtype):
        obj = copy(self)
        obj.instance = instance
        return obj


def create_cache(app, url):
    if isinstance(url, Cache):
        return url
    scheme, _, _ = parse_store_url(url)
    dotted_path = data_caches.get(scheme)
    if not dotted_path:
        raise ImproperlyConfigured('%s cache not available' % scheme)
    store_class = module_attribute(dotted_path)
    if not store_class:
        raise ImproperlyConfigured('"%s" store not available' % dotted_path)
    return store_class(app, scheme, url)


def register_cache(name, dotted_path):
    """Register a new :class:`.Cache` with ``name`` which
    can be found at the python ``dotted_path``.
    """
    data_caches[name] = dotted_path


register_cache('dummy', 'lux.core.cache.DummyCache')
register_cache('redis', 'lux.core.cache.RedisCache')


clear_cache = '''\
local keys = redis.call('keys', ARGV[1]);
for i=1,#keys,5000 do
    redis.call('del', unpack(keys, i, math.min(i+4999, #keys)))
end
return #keys
'''
