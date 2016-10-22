import sys

import pip

from pulsar import Http404
from pulsar.apps.wsgi import route

from lux.core import JsonRouter, GET_HEAD, app_attribute


def meta_route(f):
    f.meta = True
    return f


@app_attribute
def api_info_routes(app):
    return {}


class Info(JsonRouter):

    async def get(self, request):
        default = api_info_routes(request.app).get('', self.get_version)
        return self.json_response(request, default(request))

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
                return self.json_response(request, meta(request))
        raise Http404

    def get_version(self, request):
        return {'version': request.app.__version__}


def python_packages(request):
    return dict(_packages())


def _packages():
    yield 'python', ' '.join(sys.version.split('\n'))
    for p in pip.get_installed_distributions():
        try:
            yield p.key, p.version
        except Exception:
            pass
