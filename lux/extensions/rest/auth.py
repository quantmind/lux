from functools import partial

from pulsar.utils.importer import module_attribute
from lux.core import LuxExtension
from lux.forms import ValidationError

from .user import UserMixin
from .views.actions import AuthenticationError


auth_backend_methods = []


def auth_backend(f):
    name = f.__name__
    if name not in auth_backend_methods:
        auth_backend_methods.append(name)
    return f


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


class MultiAuthBackend(AuthBase):
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

    def __getattr__(self, method):
        if method in auth_backend_methods:
            return partial(self._execute_backend_method, method)
        else:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (type(self).__name__, method))

    def _execute_backend_method(self, method, request, *args, **kwargs):
        for backend in self.backends or ():
            result = getattr(backend, method)(request, *args, **kwargs)
            if result is not None:
                return result


class AuthenticationResponses:

    @auth_backend
    def authorize(self, request, auth):
        """Authorize an ``auth`` claim
        """
        pass

    @auth_backend
    def logout(self, request):  # pragma    nocover
        """Logout a user
        """
        pass

    @auth_backend
    def login(self, request, user):  # pragma    nocover
        """Login a user
        """
        pass

    @auth_backend
    def inactive_user_login_response(self, request, user):
        """JSON response when a non active user logs in
        """
        request.response.status_code = 403
        raise AuthenticationError('Cannot login - not active user')


class AuthUserMixin:

    # Internal Methods
    @auth_backend
    def authenticate(self, request, **params):  # pragma    nocover
        '''Authenticate user'''
        pass

    @auth_backend
    def create_user(self, request, **kwargs):  # pragma    nocover
        '''Create a standard user.'''
        pass

    @auth_backend
    def signup(self, request, **params):   # pragma    nocover
        """Signup a new ``user``
        """
        pass

    @auth_backend
    def signup_confirm(self, request, key):
        """Confirm a new sign up
        """
        pass

    @auth_backend
    def signup_confirmation(self, request, user):
        """Create a new signup confirmation
        """
        pass

    @auth_backend
    def create_superuser(self, request, **kwargs):  # pragma    nocover
        '''Create a user with *superuser* permissions.'''
        pass

    @auth_backend
    def get_user(self, request, **kwargs):  # pragma    nocover
        '''Retrieve a user.'''
        pass


class AuthenticationKeyMixin:

    @auth_backend
    def create_auth_key(self, request, user, **kw):
        """Create an authentication key for ``user``"""
        pass

    @auth_backend
    def confirm_auth_key(self, request, auth_key, **kw):
        '''Confirm an authentication key'''
        pass

    @auth_backend
    def password_recovery(self, request, email):
        '''Password recovery method via email
        '''
        pass

    @auth_backend
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
    @auth_backend
    def create_token(self, request, user, **kwargs):  # pragma    nocover
        '''Create an athentication token for ``user``'''
        pass

    @auth_backend
    def set_password(self, request, password, **kwargs):
        '''Set a new password for user'''
        pass

    @auth_backend
    def has_permission(self, request, resource, action):  # pragma    nocover
        '''Check if the given request has permission over ``resource``
        element with permission ``action``
        '''
        pass

    @auth_backend
    def get_permissions(self, request, resource,
                        actions=None):  # pragma    nocover
        '''Get a dictionary of permissions for the given resource
        '''
        pass
