"""Backends for Browser based Authentication
"""
import uuid
from urllib.parse import urlencode

from pulsar import ImproperlyConfigured, HttpException
from pulsar.utils.httpurl import is_absolute_uri, HTTPError

from lux import Parameter, raise_http_error, Http401, HttpRedirect
from lux.extensions.angular import add_ng_modules

from .mixins import jwt, SessionBackendMixin
from .registration import RegistrationMixin
from .. import (AuthenticationError, AuthBackend, luxrest,
                User, Session, ModelMixin)
from ..htmlviews import ForgotPassword, Login, Logout, SignUp


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

    def on_html_document(self, app, request, doc):
        if is_absolute_uri(app.config['API_URL']):
            add_ng_modules(doc, ('lux.restapi',))
        else:
            add_ng_modules(doc, ('lux.webapi',))


class ApiSessionBackend(SessionBackendMixin,
                        ModelMixin,
                        BrowserBackend):
    """Authenticating against a RESTful HTTP API.

    The workflow for authentication is the following:

    * Redirect the authentication to the remote api
    * If successful obtain the JWT token from the response
    * Create the user from decoding the JWT payload
    * create the session with same id as the token id and set the user as
      session key
    * Save the session in cache and return the original encoded token
    """
    permissions_url = None
    """url for user permissions.

    This can be a remote or internal url.
    """
    users_url = {'id': 'users',
                 'username': 'users',
                 'email': 'users',
                 'auth_key': 'users/authkey'}

    def api_sections(self, app):
        """Does not provide any view to the api. Important!
        """
        return ()

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
            # client = request.get_client_address()
            response = api.post('authorizations', data=data)
            raise_http_error(response)
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
            response = api.post('authorizations/signup', data=data)
            if response.status_code == 201:
                return User(response.json())
            else:
                response.raise_for_status()

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
        app = request.app
        session = app.cache_server.get_json(self._key(key))
        if session:
            session = Session(session)
            if session.user:
                # Check if the token is still a valid one
                api = request.app.api(request)
                response = api.head('authorizations')
                try:
                    raise_http_error(response)
                except Http401:  # 401, redirect to login
                    url = request.config['LOGIN_URL']
                    request.cache.session = self.create_session(request)
                    raise HttpRedirect(url)
                session.user = User(session.user)
            return session

    def session_save(self, request, session):
        data = session.all()
        if session.user:
            data['user'] = session.user.all()
        request.app.cache_server.set_json(self._key(session.id), data)

    def on_html_document(self, app, request, doc):
        BrowserBackend.on_html_document(self, app, request, doc)
        if request.method == 'GET':
            session = request.cache.session
            if session and session.user:
                doc.head.add_meta(name="user-token", content=session.encoded)

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
        except HTTPError as exc:
            if exc.code == 401 and request.session.user.is_authenticated():
                request.cache.auth_backend.logout(request)
                raise HttpRedirect(request.config['LOGIN_URL']) from exc
            else:
                raise

        return response.json()
