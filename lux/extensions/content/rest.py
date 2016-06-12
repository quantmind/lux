import logging

from pulsar import Http404
from pulsar.apps.wsgi import route

from lux.core import GET_HEAD
from lux.extensions.rest import CRUD


logger = logging.getLogger('lux.extensions.content')


def check_permission_dict(group, action):
    return {
        'action': action,
        'args': ('group', group)
    }


class ContentCRUD(CRUD):
    """REST API view for content
    """
    def query(self, request, *args, check_permission=None, **kwargs):
        group = request.urlargs.get('group')
        if group:
            if check_permission and not isinstance(check_permission, dict):
                check_permission = check_permission_dict(group,
                                                         check_permission)
            kwargs['group'] = group
        return super().query(request, *args,
                             check_permission=check_permission,
                             **kwargs)

    def collection_data(self, request, *filters, **params):
        params['priority:gt'] = 0
        if not group:
            raise Http404
        filters = content_filters(group, 'read')

        data = self.model.collection_data(
            request,
            load_only=('title', 'description', 'slug', 'url'),
            sortby=['title:asc', 'order:desc'],
            **content_filters(group, 'read', True)
        )

    @route('_links', method=('get', 'head', 'options'), position=-1)
    def _links(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=GET_HEAD)
            return request.response
        data = self.model.collection_data(
            request,
            load_only=('title', 'description', 'slug', 'url'),
            sortby=['title:asc', 'order:desc'],
            **{'order:gt': 0}
        )
        return self.json_response(request, data)
