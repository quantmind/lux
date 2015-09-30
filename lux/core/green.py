from pulsar.apps.greenio import wait


class WsgiGreen:
    '''Wraps a Wsgi application to be executed on a pool of greenlet
    '''
    def __init__(self, wsgi, pool):
        self.wsgi = wsgi
        self.pool = pool
        self.wait = wait

    def __call__(self, environ, start_response):
        return self.pool.submit(self._green_handler, environ, start_response)

    def _green_handler(self, environ, start_response):
        # Running on a greenlet worker
        return self.wait(self.wsgi(environ, start_response))


class GreenStream:
    __slots__ = ('stream',)

    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, name):
        value = getattr(self.stream, name)
        if getattr(value, '__self__', None) is self.stream:
            return _green(value)
        return value


class _green:
    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value

    def __getattr__(self, name):
        return getattr(self.value, name)

    def __call__(self, *args, **kwargs):
        return wait(self.value(*args, **kwargs))


def green_body(environ, start_response):

    if environ['wsgi.input']:
        environ['wsgi.input'] = GreenStream(environ['wsgi.input'])
