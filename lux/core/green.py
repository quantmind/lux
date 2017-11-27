from pulsar.apps.greenio.wsgi import GreenStream
from pulsar.apps.greenio import wait
from pulsar.apps.wsgi import wsgi_request, handle_wsgi_error
from pulsar.api import Http404


class Handler:

    def __init__(self, app, router):
        self.app = app
        self.router = router
        self.wait = wait if app.green_pool else pass_through

    def __call__(self, environ, start_response):
        pool = self.app.green_pool
        if pool and not pool.in_green_worker:
            return pool.submit(self._call, pool, environ, start_response)
        else:
            return self._call(pool, environ, start_response)

    def _call(self, pool, environ, start_response):
        if pool:
            wsgi_input = environ['wsgi.input']
            if wsgi_input and not isinstance(wsgi_input, GreenStream):
                environ['wsgi.input'] = GreenStream(wsgi_input)

        request = wsgi_request(environ)
        path = request.path
        try:
            self.app.on_request(data=request)
            hnd = self.router.resolve(path, request.method)
            if hnd:
                request.cache.set('app_handler', hnd.router)
                request.cache.set('urlargs', hnd.urlargs)
                response = self.wait(hnd.handler(request))
            else:
                raise Http404

        except Exception as exc:
            response = handle_wsgi_error(environ, exc)

        try:
            self.app.fire_event('on_response', data=(request, response))
        except Exception as exc:
            response = handle_wsgi_error(environ, exc)

        response.start(environ, start_response)
        return response


def pass_through(response):
    return response
