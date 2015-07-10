'''Backends for Browser based Authentication
'''
import uuid

from pulsar import ImproperlyConfigured
from pulsar.utils.httpurl import is_absolute_uri

from lux import Parameter
from lux.extensions.angular import add_ng_modules
from lux.extensions.rest import AuthenticationError, AuthBackend, luxrest
from lux.extensions.rest.backends import jwt, SessionBackendMixin

from .user import (User, Session, Login, LoginPost, Logout, SignUp,
                   ForgotPassword)


def auth_router(api, url, Router, path=None):
    if hasattr(Router, 'post'):
        # The Router handles post data, create an action for a web api
        action = luxrest('', path=url)
    else:
        # The Router does not handle post data, create an action for a rest api
        action = luxrest(api, name='authorizations_url')
        if path is None:
            path = url
        if path:
            action['path'] = path
    return Router(url, form_enctype='application/json', form_action=action)


class BrowserBackend(AuthBackend):
    '''Authentication backend for rendering Forms in the Browser

    It can be used by web servers delegating authentication to a backend API
    or handling authentication on the same site.

    This backend can be used even if the ``lux.extensions.cms`` is not used by
    your application.
    '''
    _config = [
        Parameter('LOGIN_URL', '/login', 'Url to login page', True),
        Parameter('LOGOUT_URL', '/logout', 'Url to logout', True),
        Parameter('REGISTER_URL', '/signup',
                  'Url to register with site', True),
        Parameter('RESET_PASSWORD_URL', '/reset-password',
                  'If given, add the router to handle password resets',
                  True)
    ]
    LoginRouter = Login
    LogoutRouter = None
    SignUpRouter = SignUp
    ForgotPasswordRouter = ForgotPassword

    def middleware(self, app):
        middleware = []
        cfg = app.config
        api = cfg['API_URL']

        if cfg['LOGIN_URL']:
            middleware.append(auth_router(api,
                                          cfg['LOGIN_URL'],
                                          self.LoginRouter, False))

        if cfg['LOGOUT_URL'] and self.LogoutRouter:
            middleware.append(auth_router(api,
                                          cfg['LOGOUT_URL'],
                                          self.LogoutRouter))

        if cfg['REGISTER_URL']:
            middleware.append(auth_router(api,
                                          cfg['REGISTER_URL'],
                                          self.SignUpRouter))

        if cfg['RESET_PASSWORD_URL']:
            middleware.append(auth_router(api,
                                          cfg['RESET_PASSWORD_URL'],
                                          self.ForgotPasswordRouter))

        return middleware

    def on_html_document(self, app, request, doc):
        if is_absolute_uri(app.config['API_URL']):
            add_ng_modules(doc, ('lux.restapi', 'lux.users'))
        else:
            add_ng_modules(doc, ('lux.webapi', 'lux.users'))


class ApiSessionBackend(SessionBackendMixin,
                        BrowserBackend):
    '''An Mixin for authenticating against a RESTful HTTP API.

    This mixin should be used when the API_URL is remote and therefore
    the API middleware is installed in the current application.

    The workflow for authentication is the following:

    * Redirect the authentication to the remote api
    * If successful obtain the JWT token from the response
    * Create the user from decoding the JWT payload
    * create the session with same id as the token id and set the user as
      session key
    * Save the session in cache and return the original encoded token
    '''
    users_url = {'id': 'users',
                 'username': 'users/username',
                 'email': 'users/email'}

    LoginRouter = LoginPost
    LogoutRouter = Logout

    def get_user(self, request, **kw):
        api = request.app.api
        for name in ('username', 'id', 'email'):
            value = kw.get(name)
            if not value:
                continue
            url = self.users_url.get(name)
            if not url:
                return
            response = api.get('%s/%s' % url, value)
            if response.status_code == 200:
                return response.json()

    def authenticate(self, request, **data):
        if not jwt:
            raise ImproperlyConfigured('JWT library not available')
        api = request.app.api
        try:
            # TODO: add address from request
            # client = request.get_client_address()
            response = api.post('authorizations', data=data)
            if response.status_code == 201:
                token = response.json().get('token')
                payload = jwt.decode(token, verify=False)
                user = User(payload)
                user.encoded = token
                return user
            else:
                response.raise_for_status()

        except Exception:
            if data.get('username'):
                raise AuthenticationError('Invalid username or password')
            elif data.get('email'):
                raise AuthenticationError('Invalid email or password')
            else:
                raise AuthenticationError('Invalid credentials')

    def create_session(self, request, user=None):
        '''Login and return response
        '''
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
                session.user = User(session.user)
            return session

    def session_save(self, request, session):
        data = session.all()
        if session.user:
            data['user'] = session.user.all()
        request.app.cache_server.set_json(self._key(session.id), data)

    def _key(self, id):
        return 'session:%s' % id
