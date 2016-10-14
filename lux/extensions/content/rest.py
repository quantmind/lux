import logging

from pulsar.apps.wsgi import route

from lux.core import GET_HEAD, Resource
from lux.extensions.rest import CRUD


logger = logging.getLogger('lux.extensions.content')


def check_permission_dict(group, action):
    return {
        'action': action,
        'args': (group,)
    }


class ContentCRUD(CRUD):
    """REST API view for content
    """
    @route('<path:slug>',
           method=('get', 'post', 'put', 'delete', 'head', 'options'))
    def read_update_delete(self, request):
        return super().read_update_delete(request)

    @route('_links', method=('get', 'head', 'options'))
    def _links(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=GET_HEAD)
            return request.response
        data = self.get_list(
            request,
            load_only=('title', 'description', 'slug', 'url'),
            sortby=['title:asc', 'order:desc'],
            check_permission=Resource.rest(request, 'read',
                                           self.model.fields(),
                                           pop=1, list=True),
            **{'order:gt': 0, 'priority:gt': 0}
        )
        return self.json_response(request, data)
