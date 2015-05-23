from pulsar.apps.data import Store, register_store, create_store


class DummyStore(Store):

    def ping(self):
        return True

    def client(self):
        return self

    def set(self, key, value, **params):
        pass

    def get(self, key):
        pass

    def hmset(self, key, iterable):
        pass

    def hmget(self, key, *fields):
        pass


register_store('dummy', 'lux.core.cache.DummyStore')
