"""Backends for Browser based Authentication
"""
import uuid
from urllib.parse import urlencode

from pulsar import ImproperlyConfigured, HttpException
from pulsar.utils.httpurl import is_absolute_uri

from lux import Parameter, Http401, PermissionDenied, Http404, HttpRedirect

from .mixins import jwt, SessionBackendMixin
from .registration import RegistrationMixin
from .. import (AuthenticationError, AuthBackend, luxrest,
                User, Session, ModelMixin)
from ..htmlviews import ForgotPassword, Login, Logout, SignUp


NotAuthorised = (Http401, PermissionDenied)


def auth_router(api_url, url, Router, path=None):
    params = {'form_enctype': 'application/json'}
    if is_absolute_uri(api_url) and hasattr(Router, 'post'):
        action = luxrest('', path=url)
    else:
        params['post'] = None
        action = luxrest(api_url, name='authorizations_url')

    params['form_action'] = action
    if path is None:
        path = url
    if path:
        action['path'] = path
    return Router(url, **params)


class BrowserBackend(RegistrationMixin,
                     AuthBackend):
    """Authentication backend for rendering Forms in the Browser

    It can be used by web servers delegating authentication to a backend API
    or handling authentication on the same site.
    """
    _config = [
        Parameter('LOGIN_URL', '/login', 'Url to login page', True),
        Parameter('LOGOUT_URL', '/logout', 'Url to logout', True),
        Parameter('REGISTER_URL', '/signup',
                  'Url to register with site', True),
        Parameter('TOS_URL', '/tos',
                  'Terms of Service url',
                  True),
        Parameter('PRIVACY_POLICY_URL', '/privacy-policy',
                  'The url for the privacy policy, required for signups',
                  True)
    ]
    LoginRouter = Login
    LogoutRouter = Logout
    SignUpRouter = SignUp
    ForgotPasswordRouter = ForgotPassword

    def middleware(self, app):
        middleware = []
        cfg = app.config
        api_url = cfg['API_URL']

        if cfg['LOGIN_URL']:
            middleware.append(auth_router(api_url,
                                          cfg['LOGIN_URL'],
                                          self.LoginRouter, False))

        if cfg['LOGOUT_URL'] and self.LogoutRouter:
            middleware.append(auth_router(api_url,
                                          cfg['LOGOUT_URL'],
                                          self.LogoutRouter))

        if cfg['REGISTER_URL']:
            middleware.append(auth_router(api_url,
                                          cfg['REGISTER_URL'],
                                          self.SignUpRouter))

        if cfg['RESET_PASSWORD_URL']:
            middleware.append(auth_router(api_url,
                                          cfg['RESET_PASSWORD_URL'],
                                          self.ForgotPasswordRouter))

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
    users_url = {'id': 'users',
                 'username': 'users',
                 'email': 'users',
                 'auth_key': 'users/authkey'}

    def get_user(self, request, **kw):
        """Get User from username, id or email or authentication key.
        """
        api = request.app.api(request)
        for name, url in self.users_url.items():
            value = kw.get(name)
            if not value:
                continue
            response = api.get(url, data=kw)
            if response.status_code == 200:
                data = response.json()
                if data['total'] == 1:
                    return User(data['result'][0])

    def authenticate(self, request, **data):
        if not jwt:
            raise ImproperlyConfigured('JWT library not available')
        api = request.app.api(request)
        try:
            # TODO: add address from request
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

    def create_user(self, request, **data):
        """Create a new user from the api
        """
        api = request.app.api(request)
        try:
            # TODO: add address from request
            # client = request.get_client_address()
            response = api.post(self.signup_url, data=data)
            if response.status_code == 201:
                return User(response.json())

        except Exception:
            if data.get('username'):
                raise AuthenticationError('Invalid username or password')
            elif data.get('email'):
                raise AuthenticationError('Invalid email or password')
            else:
                raise AuthenticationError('Invalid credentials')

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
