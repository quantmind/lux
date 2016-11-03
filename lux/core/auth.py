from functools import partial
from importlib import import_module

from pulsar import PermissionDenied, Http401
from pulsar.utils.structures import inverse_mapping
from pulsar.utils.importer import module_attribute
from pulsar.apps.wsgi import wsgi_request
from pulsar.utils.pep import to_bytes

from lux.utils.data import as_tuple

from .extension import Parameter
from .user import Anonymous


ACTIONS = {'read': 1,
           'create': 2,
           'update': 3,
           'delete': 4}

EMPTY_DICT = {}

ACTION_IDS = dict(inverse_mapping(ACTIONS))

UNUSABLE_PASSWORD = '!'

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
                response = backend_method(response) or response
        return response

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
                wait = request.app.green_pool.wait
                result = wait(backend_method(request, *args, **kwargs))
                if result is not None:
                    return result
        default = getattr(self, 'default_%s' % method, None)
        if hasattr(default, '__call__'):
            return default(request, *args, **kwargs)


class PasswordMixin:
    '''Adds password encryption to an authentication backend.

    It has two basic methods,
    :meth:`.encrypt` and :meth:`.decrypt`.
    '''
    def on_config(self, app):
        cfg = app.config
        self.encoding = cfg['ENCODING']
        self.secret_key = cfg['PASSWORD_SECRET_KEY'].encode()
        ckwargs = cfg['CRYPT_ALGORITHM']
        if not isinstance(ckwargs, dict):
            ckwargs = dict(module=ckwargs)
        self.ckwargs = ckwargs.copy()
        self.crypt_module = import_module(self.ckwargs.pop('module'))

    def encrypt(self, string_or_bytes):
        '''Encrypt ``string_or_bytes`` using the algorithm specified
        in the :setting:`CRYPT_ALGORITHM` setting.

        Return an encrypted string
        '''
        b = to_bytes(string_or_bytes, self.encoding)
        p = self.crypt_module.encrypt(b, self.secret_key, **self.ckwargs)
        return p.decode(self.encoding)

    def crypt_verify(self, encrypted, raw):
        '''Verify if the ``raw`` string match the ``encrypted`` string
        '''
        return self.crypt_module.verify(to_bytes(encrypted),
                                        to_bytes(raw),
                                        self.secret_key,
                                        **self.ckwargs)

    def decrypt(self, string_or_bytes):
        b = to_bytes(string_or_bytes, self.encoding)
        p = self.crypt_module.decrypt(b, self.secret_key)
        return p.decode(self.encoding)

    @backend_action
    def password(self, request, raw_password=None):
        '''Return an encrypted password
        '''
        if raw_password:
            return self.encrypt(raw_password)
        else:
            return UNUSABLE_PASSWORD


class Resource:
    """A resource to check permission for
    """
    def __init__(self, resource, action, fields=None):
        self.resource = resource
        self.action = action
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

    def permissions(self, request):
        """Permissions for this :class:`.Resource`

        Return a tuple of fields names or False
        """
        get = request.cache.auth_backend.get_permissions
        resources = [self.resource]
        for name in self.fields or ():
            resources.append('%s:%s' % (self.resource, name))
        perms = get(request, resources, self.action)
        if perms and perms.get(self.resource, EMPTY_DICT).get(self.action):
            return tuple(
                (
                    name for name in self.fields or () if
                    perms.get('%s:%s' % (self.resource, name)).get(self.action)
                )
            )
        return False
