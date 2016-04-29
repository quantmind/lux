"""Backends for Browser based Authentication
"""
import uuid
from urllib.parse import urlencode

from pulsar import (ImproperlyConfigured, HttpException, Http401,
                    PermissionDenied, Http404, HttpRedirect)

from .mixins import jwt, SessionBackendMixin
from .registration import RegistrationMixin
from .. import (AuthenticationError, AuthBackend,
                User, Session, ModelMixin)
from ..views import browser


NotAuthorised = (Http401, PermissionDenied)


class BrowserBackend(RegistrationMixin,
                     AuthBackend):
    """Authentication backend for rendering Forms in the Browser

    It can be used by web servers delegating authentication to a backend API
    or handling authentication on the same site.
    """
    LoginRouter = browser.Login
    LogoutRouter = browser.Logout
    SignUpRouter = browser.SignUp
    ForgotPasswordRouter = browser.ForgotPassword

    def middleware(self, app):
        middleware = []
        cfg = app.config

        if cfg['LOGIN_URL']:
            middleware.append(self.LoginRouter(cfg['LOGIN_URL']))

        if cfg['LOGOUT_URL']:
            middleware.append(self.LogoutRouter(cfg['LOGOUT_URL']))

        if cfg['REGISTER_URL']:
            middleware.append(self.SignUpRouter(cfg['REGISTER_URL']))

        if cfg['RESET_PASSWORD_URL']:
            middleware.append(
                self.ForgotPasswordRouter(cfg['RESET_PASSWORD_URL']))

        return middleware


class ApiSessionBackend(SessionBackendMixin,
                        ModelMixin,
                        BrowserBackend):
    """Authenticating against a RESTful HTTP API.

    This backend requires a real cache backend, it cannot work with dummy
    cache and will raise an error.

    The workflow for authentication is the following:

    * Redirect the authentication to the Rest API
    * If successful obtain the ``token`` from the response
    * Create the user from decoding the JWT payload
    * Create the session with same id as the token id and set the user as
      session key
    * Save the session in cache and return the original encoded token
    """
    permissions_url = 'user/permissions'
    """url for user permissions.
    """
    signup_url = 'authorizations/signup'
    """url for signup a user.
    """
    reset_password_url = 'authorizations/reset-password'
    """url for resetting password
    """
    auth_keys_url = 'authorizations/keys'
    """url for authorization keys
    """
    users_url = 'users'

    def authenticate(self, request, **data):
        if not jwt:
            raise ImproperlyConfigured('JWT library not available')
        api = request.app.api(request)
        try:
            response = api.post('authorizations', data=data)
            token = response.json().get('token')
            payload = jwt.decode(token, verify=False)
            user = User(payload)
            user.encoded = token
            return user

        except (AuthenticationError, HttpException):
            raise
        except Exception:
            if data.get('username'):
                raise AuthenticationError('Invalid username or password')
            elif data.get('email'):
                raise AuthenticationError('Invalid email or password')
            else:
                raise AuthenticationError('Invalid credentials')

    def signup(self, request, **data):
        """Create a new user from the api
        """
        api = request.app.api(request)
        try:
            response = api.post(self.signup_url, data=data)
            if response.status_code == 201:
                return response.json()
        except Exception:
            if data.get('username'):
                raise AuthenticationError('Invalid username or password')
            elif data.get('email'):
                raise AuthenticationError('Invalid email or password')
            else:
                raise AuthenticationError('Invalid credentials')

    def signup_confirm(self, request, key):
        api = request.app.api(request)
        response = api.post('%s/%s' % (self.signup_url, key))
        return response.json()

    def signup_confirmation(self, request, username):
        api = request.app.api(request)
        response = api.post('authorizations/%s' % username)
        return response.json()

    def get_permissions(self, request, resources, actions=None):
        return self._get_permissions(request, resources, actions)

    def has_permission(self, request, resource, action):
        """Implement :class:`~AuthBackend.has_permission` method
        """
        data = self._get_permissions(request, resource, action)
        resource = data.get(resource)
        if resource:
            return resource.get(action, False)
        return False

    def password_recovery(self, request, **params):
        api = request.app.api(request)
        response = api.post(self.reset_password_url, data=params)
        return response.json()

    def set_password(self, request, password, user=None, auth_key=None):
        api = request.app.api(request)
        if not auth_key:
            raise AuthenticationError('Missing authentication key')
        url = '%s/%s' % (self.reset_password_url, auth_key)
        data = {'password': password, 'password_repeat': password}
        response = api.post(url, data=data)
        return response.json()

    def confirm_auth_key(self, request, key, **kw):
        api = request.app.api(request)
        try:
            api.head('%s/%s' % (self.auth_keys_url, key))
        except Http404:
            return False
        return True

    def create_session(self, request, user=None):
        """Login and return response
        """
        if user:
            user = User(user)
            session = Session(id=user.pop('token_id'),
                              expiry=user.pop('exp'),
                              user=user)
            session.encoded = session.user.pop('encoded')
        else:
            session = Session(id=uuid.uuid4().hex)
        return session

    def get_session(self, request, key):
        """Get the session at key from the cache server
        """
        app = request.app
        session = app.cache_server.get_json(self._key(key))
        if session:
            session = Session(session)
            if session.user:
                user = User(session.user)
                # Check if the token is still a valid one
                api = request.app.api(request)
                try:
                    if not session.encoded:
                        raise Http401
                    api.head('authorizations', token=session.encoded)
                except NotAuthorised:
                    handle_401(request, user)
                session.user = user
            return session

    def session_save(self, request, session):
        data = session.all()
        if session.user:
            data['user'] = session.user.all()
        store = request.app.cache_server
        if store.name == 'dummy':
            request.logger.error('Cannot use dummy cache with %s backend',
                                 self.__class__.__name__)
        store.set_json(self._key(session.id), data)

    def _key(self, id):
        return 'session:%s' % id

    def _get_permissions(self, request, resources, actions=None):
        assert self.permissions_url, "permission url not available"
        if not isinstance(resources, (list, tuple)):
            resources = (resources,)
        query = [('resource', resource) for resource in resources]
        if actions:
            if not isinstance(actions, (list, tuple)):
                actions = (actions,)
            query.extend((('action', action) for action in actions))
        query = urlencode(query)
        api = request.app.api(request)
        try:
            response = api.get('%s?%s' % (self.permissions_url, query))
        except NotAuthorised:
            handle_401(request)

        return response.json()


def handle_401(request, user=None):
    """When the API respond with a 401 logout and redirect to login
    """
    user = user or request.session.user
    if user.is_authenticated():
        request.cache.auth_backend.logout(request)
        raise HttpRedirect(request.config['LOGIN_URL'])
    else:
        raise Http404
