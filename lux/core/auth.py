from pulsar.utils.structures import AttributeDictionary

from lux.utils.data import as_tuple

from .extension import LuxExtension

ALL_PERMISSIONS = ('read', 'create', 'update', 'delete')

auth_backend_actions = set()


def backend_action(fun):
    name = fun.__name__
    auth_backend_actions.add(name)
    return fun


class AuthBase(LuxExtension):
    abstract = True

    def request(self, request):  # pragma    nocover
        '''Request middleware. Most backends implement this method
        '''
        pass

    @backend_action
    def has_permission(self, request, resource, action):  # pragma    nocover
        '''Check if the given request has permission over ``resource``
        element with permission ``action``
        '''
        pass

    @backend_action
    def get_permissions(self, request, resources,
                        actions=None):  # pragma    nocover
        """Get a dictionary of permissions for the given resource"""
        perm = dict(((p, True) for p in ALL_PERMISSIONS))
        return dict(((r, perm.copy()) for r in as_tuple(resources)))


class SimpleBackend(AuthBase):

    def has_permission(self, request, resource, action):
        return True
