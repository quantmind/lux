import asyncio


def maybe_green(app, callable, *args, **kwargs):
    """Run a ``callable`` in the green pool if needed

    :param app: lux application
    :param callable: callable to execute
    :param args:
    :param kwargs:
    :return: a synchronous or asynchronous result
    """
    pool = app.green_pool
    if pool:
        if pool.in_green_worker:
            return pool.wait(callable(*args, **kwargs))
        elif not asyncio.iscoroutinefunction(callable):
            return pool.submit(callable, *args, **kwargs)
    return callable(*args, **kwargs)


class GreenPubSub:

    def __init__(self, pool, pubsub):
        self.pool = pool
        self._pubsub = pubsub

    def __repr__(self):
        return repr(self._pubsub)
    __str__ = __repr__

    @property
    def _protocol(self):
        return self._pubsub._protocol

    def publish(self, channel, message):
        return self.pool.wait(self._pubsub.publish(channel, message))

    def subscribe(self, channel, *channels):
        return self.pool.wait(self._pubsub.subscribe(channel, *channels))

    def channels(self, pattern=None):
        return self.pool.wait(self._pubsub.channels(pattern=pattern))

    def add_client(self, client):
        self._pubsub.add_client(client)
