import json
from functools import wraps

from pulsar.apps.data import parse_store_url, create_store
from pulsar.utils.importer import module_attribute
from pulsar.utils.string import to_string
from pulsar import ImproperlyConfigured


data_caches = {}


class Cache:

    def __init__(self, app, name, url):
        self.app = app
        self.name = name

    def ping(self):
        return True

    def set(self, key, value, **params):
        pass

    def get(self, key):
        pass

    def hmset(self, key, iterable):
        pass

    def hmget(self, key, *fields):
        pass

    def set_json(self, key, value, timeout=None):
        value = json.dumps(to_string(value))
        self.set(key, value, timeout=timeout)

    def get_json(self, key):
        value = self.get(key)
        if value is not None:
            try:
                return json.loads(to_string(value))
            except Exception:
                self.app.logger.warning('Could not convert to JSON: %s',
                                        value)


class RedisCache(Cache):

    def __init__(self, app, scheme, url):
        super().__init__(app, scheme, url)
        if app.green_pool:
            from pulsar.apps.greenio import wait
            self._wait = wait
            self.client = create_store(url).client()
        else:
            import redis
            self.client = redis.StrictRedis.from_url(url)
            raise NotImplementedError

    def set(self, key, value, timeout=None):
        self._wait(self.client.set(key, value, timeout))

    def get(self, key):
        return self._wait(self.client.get(key))

    def hmset(self, key, iterable, timeout=None):
        self._wait(self.client.hmset(key, iterable, timeout))

    def hmget(self, key, *fields):
        return self._wait(self.client.hmset(key, *fields))

    def _wait(self, value):
        return value


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
    '''Register a new :class:`.Cache` with ``name`` which
    can be found at the python ``dotted_path``.
    '''
    data_caches[name] = dotted_path


register_cache('dummy', 'lux.core.cache.Cache')
register_cache('redis', 'lux.core.cache.RedisCache')
