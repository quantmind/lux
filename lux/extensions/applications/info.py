import sys

import pip

from pulsar import Http404
from pulsar.apps.wsgi import route, WsgiResponse

from lux.core import JsonRouter, GET_HEAD, app_attribute


@app_attribute
def api_info_routes(app):
    return {}


class Info(JsonRouter):

    async def get(self, request):
        routes = {}
        base = request.absolute_uri('/%s' % self.route.rule)
        for name in sorted(api_info_routes(request.app)):
            routes[name] = '%s/%s' % (base, name)
        return self.json_response(request, routes)

    def options(self, request):
        request.app.fire('on_preflight', request, methods=GET_HEAD)
        return request.response

    @route('<meta>', method=('get', 'head', 'options'))
    def meta(self, request):
        routes = api_info_routes(request.app)
        meta = routes.get(request.urlargs['meta'])
        if meta:
            if request.method == 'OPTIONS':
                return self.options(request)
            else:
                response = meta(request)
                if not isinstance(response, WsgiResponse):
                    response = self.json_response(request, response)
                return response
        raise Http404


def python_packages(request):
    return dict(_packages())


def _packages():
    yield 'python', ' '.join(sys.version.split('\n'))
    for p in pip.get_installed_distributions():
        try:
            yield p.key, p.version
        except Exception:   # pragma    nocover
            pass
