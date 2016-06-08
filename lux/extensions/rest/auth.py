from functools import partial

from pulsar.utils.importer import module_attribute
from pulsar.utils.structures import AttributeDictionary

from lux.core import LuxExtension
from lux.forms import ValidationError

from .user import UserMixin
from .views.actions import AuthenticationError


auth_backend_actions = set()


def backend_action(fun):
    name = fun.__name__
    auth_backend_actions.add(name)
    return fun


class Anonymous(UserMixin):

    def __repr__(self):
        return self.__class__.__name__.lower()

    def is_authenticated(self):
        return False

    def is_anonymous(self):
        return True

    def get_id(self):
        return 0


class AuthBase(LuxExtension):
    abstract = True

    def request(self, request):  # pragma    nocover
        '''Request middleware. Most backends implement this method
        '''
        pass

    def anonymous(self):
        '''Anonymous User
        '''
        return Anonymous()

    def user_agent(self, request, max_len=80):
        agent = request.get('HTTP_USER_AGENT')
        return agent[:max_len] if agent else ''

    def validate_username(self, request, username):
        request = request
        validator = module_attribute(request.config['CHECK_USERNAME'])
        if validator(request, username):
            return username
        else:
            raise ValidationError('Username not available')


class ProxyBackend:

    def __getattr__(self, method):
        if method in auth_backend_actions:
            return partial(self._execute_backend_method, method)
        else:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (type(self).__name__, method))

    def _execute_backend_method(self, method, request, *args, **kwargs):
        return None


class MultiAuthBackend(AuthBase, ProxyBackend):
    '''Aggregate several Authentication backends
    '''
    abstract = True
    backends = None

    def request(self, request):
        # Inject self as the authentication backend
        cache = request.cache
        cache.user = self.anonymous()
        cache.auth_backend = self
        return self._execute_backend_method('request', request)

    def has_permission(self, request, resource, action):
        has = self._execute_backend_method('has_permission',
                                           request, resource, action)
        return True if has is None else has

    def __iter__(self):
        return iter(self.backends or ())

    def _execute_backend_method(self, method, request, *args, **kwargs):
        for backend in self.backends or ():
            backend_method = getattr(backend, method, None)
            if backend_method:
                result = backend_method(request, *args, **kwargs)
                if result is not None:
                    return result


class AuthenticationResponses:

    @backend_action
    def authorize(self, request, auth):
        """Authorize an ``auth`` claim
        """
        pass

    @backend_action
    def logout(self, request):  # pragma    nocover
        """Logout a user
        """
        pass

    @backend_action
    def login(self, request, user):  # pragma    nocover
        """Login a user
        """
        pass

    @backend_action
    def inactive_user_login_response(self, request, user):
        """JSON response when a non active user logs in
        """
        request.response.status_code = 403
        raise AuthenticationError('Cannot login - not active user')


class AuthUserMixin:

    # Internal Methods
    @backend_action
    def authenticate(self, request, **params):  # pragma    nocover
        '''Authenticate user'''
        pass

    @backend_action
    def create_user(self, request, **kwargs):  # pragma    nocover
        '''Create a standard user.'''
        pass

    @backend_action
    def signup(self, request, **params):   # pragma    nocover
        """Signup a new ``user``
        """
        pass

    @backend_action
    def signup_confirm(self, request, key):
        """Confirm a new sign up
        """
        pass

    @backend_action
    def signup_confirmation(self, request, user):
        """Create a new signup confirmation
        """
        pass

    @backend_action
    def create_superuser(self, request, **kwargs):  # pragma    nocover
        '''Create a user with *superuser* permissions.'''
        pass

    @backend_action
    def get_user(self, request, **kwargs):  # pragma    nocover
        '''Retrieve a user.'''
        pass


class AuthenticationKeyMixin:

    @backend_action
    def create_auth_key(self, request, user, **kw):
        """Create an authentication key for ``user``"""
        pass

    @backend_action
    def confirm_auth_key(self, request, auth_key, **kw):
        '''Confirm an authentication key'''
        pass

    @backend_action
    def password_recovery(self, request, email):
        '''Password recovery method via email
        '''
        pass

    @backend_action
    def auth_key_expiry(self, request):
        '''Expiry for a session or a token
        '''
        pass


class AuthBackend(AuthBase,
                  AuthUserMixin,
                  AuthenticationResponses,
                  AuthenticationKeyMixin):
    '''Interface for extension supporting restful methods
    '''
    @backend_action
    def create_token(self, request, user, **kwargs):  # pragma    nocover
        '''Create an athentication token for ``user``'''
        pass

    @backend_action
    def set_password(self, request, password, **kwargs):
        '''Set a new password for user'''
        pass

    @backend_action
    def has_permission(self, request, resource, action):  # pragma    nocover
        '''Check if the given request has permission over ``resource``
        element with permission ``action``
        '''
        pass

    @backend_action
    def get_permissions(self, request, resource,
                        actions=None):  # pragma    nocover
        '''Get a dictionary of permissions for the given resource
        '''
        pass


class SimpleBackend(AuthBackend):

    def has_permission(self, request, resource, action):
        return True


class AppRequest:

    def __init__(self, app, **kw):
        self.cache = AttributeDictionary(app=app, **kw)
        self.cache.auth_backend = SimpleBackend()

    @property
    def app(self):
        return self.cache.app

    def __getattr__(self, name):
        return getattr(self.app, name)
