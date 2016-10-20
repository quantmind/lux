from functools import partial

from pulsar import PermissionDenied, Http401
from pulsar.utils.structures import inverse_mapping
from pulsar.utils.importer import module_attribute
from pulsar.apps.wsgi import wsgi_request

from lux.utils.data import as_tuple

from .cache import cached
from .extension import Parameter
from .user import Anonymous


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


class AuthenticationError(ValueError):
    pass


class BackendMixin:
    """Add authentication backends to the application
    """
    _config = [
        Parameter('AUTHENTICATION_BACKENDS', [],
                  'List of python dotted paths to classes which provide '
                  'a backend for authentication.')
    ]

    def _on_config(self, config):
        self.auth_backend = MultiAuthBackend()
        for dotted_path in config['AUTHENTICATION_BACKENDS']:
            backend = module_attribute(dotted_path)
            if not backend:
                self.logger.error('Could not load backend "%s"', dotted_path)
                continue
            backend = backend()
            self.auth_backend.append(backend)
            self.bind_events(backend)


class AuthBase:

    @backend_action
    def anonymous(self, request):
        pass

    @backend_action
    def has_permission(self, request, resource, action):
        '''Check if the given request has permission over ``resource``
        element with permission ``action``
        '''
        pass

    @backend_action
    def get_permissions(self, request, resources, actions=None):
        """Get a dictionary of permissions for the given resource"""
        pass


class SimpleBackend(AuthBase):

    def has_permission(self, request, resource, action):
        return True

    def get_permissions(self, request, resources, actions=None):
        """Get a dictionary of permissions for the given resource"""
        perm = dict(((action, True) for action in ACTIONS))
        return dict(((r, perm.copy()) for r in as_tuple(resources)))


class MultiAuthBackend:
    '''Aggregate several Authentication backends
    '''
    def __init__(self):
        self.backends = []

    def append(self, backend):
        self.backends.append(backend)

    def request(self, environ, start_response=None):
        # Inject self as the authentication backend
        request = wsgi_request(environ)
        cache = request.cache
        cache.auth_backend = self
        cache.user = self.anonymous(request)
        return self._execute_backend_method('request', request)

    def response(self, environ, response):
        for backend in reversed(self.backends):
            backend_method = getattr(backend, 'response', None)
            if backend_method:
                result = backend_method(response)
                if result is not None:
                    return result

    def has_permission(self, request, resource, action):
        has = self._execute_backend_method('has_permission',
                                           request, resource, action)
        return True if has is None else has

    def default_anonymous(self, request):
        return Anonymous()

    def __iter__(self):
        return iter(self.backends)

    def __getattr__(self, method):
        if method in auth_backend_actions:
            return partial(self._execute_backend_method, method)
        else:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (type(self).__name__, method))

    def _execute_backend_method(self, method, request, *args, **kwargs):
        for backend in self:
            backend_method = getattr(backend, method, None)
            if backend_method:
                result = backend_method(request, *args, **kwargs)
                if result is not None:
                    return result
        default = getattr(self, 'default_%s' % method, None)
        if hasattr(default, '__call__'):
            return default(request, *args, **kwargs)


class Resource:
    """A resource to check permission for
    """
    def __init__(self, resource, action, fields=None):
        self.resource = resource
        self.action = action
        self.fields = fields
        self.permissions = cached(key=str(self), user=True)(self._permissions)

    @classmethod
    def rest(cls, request, action, fields=None, pop=0, list=False):
        resource = request.path[1:].replace('/', ':')
        if pop:
            resource = ':'.join(resource.split(':')[:-pop])
        if list:
            resource = '%s:*' % resource
        return cls(resource, action, fields)

    @classmethod
    def app(cls, request, action=None):
        resource = '%s%s' % (request.config['APP_NAME'], request.path)
        action = action or 'read'
        return cls(resource.replace('/', ':').lower(), action)

    def __repr__(self):
        if self.fields:
            fields = ':'.join(self.fields)
            return '%s-%s-%s' % (self.resource, self.action, fields)
        else:
            return '%s-%s' % (self.resource, self.action)
    __str__ = __repr__

    def __call__(self, request, load_only=None):
        perms = self.permissions(request)
        if perms is False:
            user = request.cache.user
            if user.is_anonymous():
                raise Http401('token')
            else:
                raise PermissionDenied
        if load_only:
            return tuple(set(perms).intersection(load_only))
        else:
            return perms

    def _permissions(self, request):
        """Permissions for this :class:`.Resource`"""
        has = request.cache.auth_backend.has_permission
        root_perm = has(request, self.resource, self.action)
        if not root_perm:
            return False

        if self.fields:
            return tuple((name for name in self.fields if
                          has(request, '%s:%s' % (self.resource, name),
                              self.action)
                          )
                         )
        else:
            return ()
