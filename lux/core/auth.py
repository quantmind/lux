from pulsar import PermissionDenied
from pulsar.utils.structures import inverse_mapping

from lux.utils.data import as_tuple

from .extension import LuxExtension

ACTIONS = {'read': 1,
           'create': 2,
           'update': 3,
           'delete': 4}

ACTION_IDS = dict(inverse_mapping(ACTIONS))

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
        pass


class SimpleBackend(AuthBase):

    def has_permission(self, request, resource, action):
        return True

    def get_permissions(self, request, resources, actions=None):
        """Get a dictionary of permissions for the given resource"""
        perm = dict(((action, True) for action in ACTIONS))
        return dict(((r, perm.copy()) for r in as_tuple(resources)))


class Resource:

    def __init__(self, resource, action=None, fields=None):
        self.resource = resource
        self.action = action or 'read'
        self.fields = fields

    @classmethod
    def rest(cls, request, action, fields=None, pop=0, list=False):
        resource = request.path[1:].replace('/', ':')
        if pop:
            resource = ':'.join(resource.split(':')[:-pop])
        if list:
            resource = '%s:*' % resource
        return cls(resource, action, fields)

    @classmethod
    def app(cls, request):
        resource = '%s%s' % (request.config['APP_NAME'], request.path)
        return cls(resource.replace('/', ':'))

    def __call__(self, request, load_only=None):
        perms = self.permissions(request)
        if not perms:
            raise PermissionDenied
        if load_only:
            return tuple(set(perms).intersection(load_only))
        else:
            return perms

    def permissions(self, request):
        """Dictionary of permissions for this :class:`.Resource`
        """
        perm = None
        permissions = request.cache.permissions
        if permissions is None:
            request.cache.permissions = permissions = {}

        if self.resource not in permissions:
            permissions[self.resource] = {}
        elif self.action in permissions[self.resource]:
            perm = permissions[self.resource][self.action]

        if perm is None:
            has = request.cache.auth_backend.has_permission
            root_perm = has(request, self.resource, self.action)
            if root_perm and self.fields:
                has = request.cache.auth_backend.has_permission
                perm = tuple((name for name in self.fields if
                              has(request, '%s:%s' % (self.resource, name),
                                  self.action)
                              )
                             )
            else:
                perm = ()
            permissions[self.resource][self.action] = perm

        return perm
