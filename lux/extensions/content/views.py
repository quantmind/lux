import logging

from pulsar.apps.wsgi import route
from pulsar.utils.httpurl import remove_double_slash

from lux.extensions import rest

from .utils import get_context_files, get_reader, get_content


logger = logging.getLogger('lux.extensions.content')


def list_filter(model, filters):
    filters['path:ne'] = remove_double_slash('/%s' % model.html_url)
    return filters


class ContentCRUD(rest.RestRouter):
    """REST API view for content
    """

    def get(self, request):
        self.check_model_permission(request, 'read')
        filters = list_filter(self.model, {})
        return self.model.collection_response(request, sortby='date:desc',
                                              **filters)

    @route('<group>', method=('get', 'options'))
    def get_group(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['GET'])
            return request.response

        self.check_model_permission(request, 'read')
        filters = list_filter(self.model, {'group': request.urlargs['group']})
        return self.model.collection_response(request, sortby='date:desc',
                                              **filters)

    @route('<group>/_links', method=('get', 'options'))
    def _links(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['GET'])
            return request.response

        filters = list_filter(self.model, {'group': request.urlargs['group'],
                                           'order:gt': 0})
        return self.model.collection_response(
            request, sortby=['title:asc', 'order:desc'], **filters)

    @route('<group>/<path:path>', method=('get', 'head', 'options'))
    def read_update(self, request):
        path = request.urlargs['path']
        group = request.urlargs['group']
        model = self.model

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', methods=['GET', 'HEAD'])
            return request.response

        content = get_content(request, group, path)

        if request.method == 'GET':
            self.check_model_permission(request, 'read', content)
            data = model.serialise(request, content)
            if data == request.response:
                return data
            return self.json(request, data)

        elif request.method == 'HEAD':
            self.check_model_permission(request, 'read', content)
            return request.response
