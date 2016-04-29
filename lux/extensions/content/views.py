import logging

from pulsar import Http404, MethodNotAllowed
from pulsar.apps.wsgi import route
from pulsar.utils.httpurl import remove_double_slash

from lux.extensions import rest

from .utils import get_context_files, get_reader, get_content


logger = logging.getLogger('lux.extensions.content')


def list_filter(model, filters):
    filters['path:ne'] = remove_double_slash('/%s' % model.html_url)
    return filters


class SnippetCRUD(rest.RestRouter):

    def get(self, request):
        ctx = {}
        for key in get_context_files(request.app):
            ctx[key] = request.absolute_uri(key)
        return self.json(request, ctx)

    @route('<key>', method=('get', 'options'))
    def _context_path(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['GET'])
            return request.response
        ctx = get_context_files(request.app)
        src = ctx.get(request.urlargs['key'])
        if not src:
            raise Http404
        app = request.app
        content = get_reader(app, src).read(src)
        return self.json(request, content.json(app))


class ContentCRUD(rest.RestRouter):

    def get(self, request):
        self.check_model_permission(request, 'read')
        filters = list_filter(self.model, {})
        return self.model.collection_response(request, sortby='date:desc',
                                              **filters)

    @route('_links', method=('get', 'options'))
    def _links(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['GET'])
            return request.response
        filters = list_filter(self.model, {'order:gt': 0})
        return self.model.collection_response(
            request, sortby=['title:asc', 'order:desc'], **filters)

    @route('<path:path>', method=('get', 'head', 'post', 'options'))
    def read_update(self, request):
        path = request.urlargs['path']
        model = self.model

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        content = get_content(request, model, path)

        if request.method == 'GET':
            self.check_model_permission(request, 'read', content)
            data = model.serialise(request, content)
            if data == request.response:
                return data

        elif request.method == 'HEAD':
            self.check_model_permission(request, 'read', content)
            return request.response

        else:
            raise MethodNotAllowed

        return self.json(request, data)
