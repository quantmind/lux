from functools import partial

from pulsar.utils.importer import module_attribute

from lux.core import AuthBase, backend_action, auth_backend_actions
from lux.forms import ValidationError

from .user import UserMixin
from .views.actions import AuthenticationError


class AuthBackendBase(AuthBase):
    abstract = True

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


class AuthBackend(AuthBackendBase,
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
