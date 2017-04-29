from importlib import import_module

from pulsar.api import PermissionDenied, Http401, BadRequest
from pulsar.utils.structures import inverse_mapping
from pulsar.utils.string import to_bytes
from pulsar.utils.log import lazyproperty

from lux.utils.data import as_tuple
import lux.utils.token as jwt
from lux.models import Component

from .user import Anonymous, ServiceUser


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


class PasswordMixin:
    '''Adds password encryption to an authentication backend.

    It has two basic methods,
    :meth:`.encrypt` and :meth:`.decrypt`.
    '''
    @lazyproperty
    def crypt_module(self):
        kwargs = self.config['CRYPT_ALGORITHM']
        if not isinstance(kwargs, dict):
            kwargs = dict(module=kwargs)
        kwargs = kwargs.copy()
        return import_module(kwargs.pop('module')), kwargs

    def encrypt(self, string_or_bytes):
        '''Encrypt ``string_or_bytes`` using the algorithm specified
        in the :setting:`CRYPT_ALGORITHM` setting.

        Return an encrypted string
        '''
        encoding = self.config['ENCODING']
        secret_key = self.config['PASSWORD_SECRET_KEY'].encode()
        b = to_bytes(string_or_bytes, encoding)
        module, kwargs = self.crypt_module
        p = module.encrypt(b, secret_key, **kwargs)
        return p.decode(encoding)

    def crypt_verify(self, encrypted, raw):
        '''Verify if the ``raw`` string match the ``encrypted`` string
        '''
        secret_key = self.config['PASSWORD_SECRET_KEY'].encode()
        module, kwargs = self.crypt_module
        return module.verify(to_bytes(encrypted), to_bytes(raw),
                             secret_key, **kwargs)

    def decrypt(self, string_or_bytes):
        secret_key = self.config['PASSWORD_SECRET_KEY'].encode()
        b = to_bytes(string_or_bytes, self.config['ENCODING'])
        p = self.crypt_module.decrypt(b, secret_key)
        return p.decode(self.encoding)

    def password(self, raw_password=None):
        '''Return an encrypted password or unusable password
        '''
        if raw_password:
            return self.encrypt(raw_password)
        else:
            return UNUSABLE_PASSWORD


class JwtMixin:

    def decode_jwt(self, request, token):
        config = self.config
        return self._decode_jwt(request, token, config['SECRET_KEY'],
                                algorithm=config['JWT_ALGORITHM'])

    def _decode_jwt(self, request, token, key=None, algorithm=None, **options):
        try:
            return jwt.decode(token, key=key, algorithm=algorithm,
                              options=options)
        except jwt.ExpiredSignature:
            request.logger.warning('JWT token has expired')
            raise Http401('Token') from None
        except jwt.DecodeError as exc:
            request.logger.warning(str(exc))
            raise BadRequest from None


class PermissionMixin:

    def has_permission(self, request, resource, action):
        '''Check if the given request has permission over ``resource``
        element with permission ``action``
        '''
        return True

    def get_permissions(self, request, resources, actions=None):
        """Get a dictionary of permissions for the given resource"""
        perm = dict(((action, True) for action in ACTIONS))
        return dict(((r, perm.copy()) for r in as_tuple(resources)))


class AuthBackend(Component, PermissionMixin, PasswordMixin, JwtMixin):
    '''Aggregate several Authentication backends
    '''
    service_user = ServiceUser
    anonymous = Anonymous

    def __init__(self, app):
        self.init_app(app)

    def on_request(self, request):
        request.cache.user = self.anonymous()

    def response(self, environ, response):
        pass

    def authenticate(self, session, **kw):
        raise AuthenticationError

    def create_user(self, session, **params):
        raise NotImplementedError


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
        get = request.app.auth.get_permissions
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
