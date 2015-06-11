from functools import wraps

from pulsar.apps.data import parse_store_url
from pulsar.utils.importer import module_attribute
from pulsar import ImproperlyConfigured


data_caches = {}


class Cache:

    def __init__(self, app, name, url):
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


class RedisCache(Cache):

    def __init__(self, app, url):
        self.app = app

    def set(self, key, value, timeout=None):
        return wait(self.client.set(key, value, timeout=timeout))

    def set(self, key):
        return wait(self.client.get(key))


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
