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
    def filters_params(self, request, *filters, **params):
        """Enhance permission check for groups
        """
        filters, params = super().filters_params(request, *filters, **params)
        if 'id' in params:
            params['slug'] = params.pop('id')
        return filters, params

    def get_list(self, request, *filters, **params):
        params['priority:gt'] = 0
        return super().get_list(request, *filters, **params)

    @route('_links', method=('get', 'head', 'options'), position=-1)
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
            **{'order:gt': 0}
        )
        return self.json_response(request, data)
