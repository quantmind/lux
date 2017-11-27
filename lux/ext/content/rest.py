from lux.core import Resource
from lux.ext.rest import RestRouter, route


def check_permission_dict(group, action):
    return {
        'action': action,
        'args': (group,)
    }


class ContentCRUD(RestRouter):
    """REST API view for content
    """
    @route('links')
    def get_links(self, request):
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

    @route('<path:slug>',
           method=('get', 'post', 'put', 'delete', 'head', 'options'))
    def read_update_delete(self, request):
        return super().read_update_delete(request)
