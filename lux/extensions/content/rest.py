import logging

from pulsar.apps.wsgi import route

from lux.extensions import rest


logger = logging.getLogger('lux.extensions.content')


class ContentCRUD(rest.RestRouter):
    """REST API view for content
    """
    @route('<group>', method=('get', 'options'))
    def get_group(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['GET'])
            return request.response

        group = request.urlargs['group']
        self.check_model_permission(request, 'read', group=group)
        filters = {'sortby': 'date:desc'}
        return self.model.collection_response(request, **filters)

    @route('<group>/_links', method=('get', 'options'))
    def _links(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['GET'])
            return request.response

        filters = {
            'order:gt': 0,
            'sortby': ['title:asc', 'order:desc']
        }
        return self.model.collection_response(request, **filters)

    @route('<group>/<path:path>', method=('get', 'head', 'options'))
    def read_update(self, request):
        path = request.urlargs['path']
        group = request.urlargs['group']
        model = self.model

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['GET', 'HEAD'])
            return request.response

        self.check_model_permission(request, 'read', group=group)

        content = model.get_instance(request, '%s/%s' % (group, path))

        if request.method == 'GET':
            data = model.serialise(request, content)
            if data == request.response:
                return data
            return self.json_response(request, data)

        elif request.method == 'HEAD':
            return request.response

    def check_model_permission(self, request, level, model=None, group=None):
        if not model and group:
            model = 'contents:%s' % group
        return super().check_model_permission(request, level, model)
