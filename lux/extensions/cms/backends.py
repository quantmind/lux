'''Backends for Browser based Authentication
'''
from pulsar import ImproperlyConfigured
from pulsar.utils.httpurl import is_absolute_uri

from lux import Parameter
from lux.extensions.angular import add_ng_modules
from lux.extensions.rest import AuthenticationError, AuthBackend, luxrest
from lux.extensions.rest.backends import (CacheSessionMixin, jwt,
                                          SessionBackendMixin)

from .user import User, Login, LoginPost, SignUp, ForgotPassword


def auth_router(api, url, Router):
    if hasattr(Router, 'post'):
        # The Router handles post data, create an action for a web api
        action = luxrest('', path=url)
    else:
        # The Router does not handle post data, create an action for a rest api
        action = luxrest(api, name='authorizations_url')
    return Router(url, form_enctype='application/json', form_action=action)


class BrowserBackend(AuthBackend):
    '''Authentication backend for rendering Forms in the Browser

    It can be used by web servers delegating authentication to a backend API
    or handling authentication on the same site.
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
    SignUpRouter = SignUp
    ForgotPasswordRouter = ForgotPassword

    def middleware(self, app):
        middleware = []
        cfg = app.config
        api = cfg['API_URL']

        if cfg['LOGIN_URL']:
            middleware.append(auth_router(api,
                                          cfg['LOGIN_URL'],
                                          self.LoginRouter))

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


class ApiSessionBackend(CacheSessionMixin,
                        SessionBackendMixin,
                        BrowserBackend):
    '''An Mixin for authenticating against a RESTful HTTP API.

    This mixin should be used when the API_URL is remote and therefore
    not API is installed in the current application.
    '''
    users_url = {'id': 'users',
                 'username': 'users/username',
                 'email': 'users/email'}

    LoginRouter = LoginPost

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
            response = api.post('authorizations', data=data)
            if response.status_code == 201:
                token = response.json().get('token')
                payload = jwt.decode(token, verify=False)
                return User(payload)
            else:
                response.raise_for_status()

        except Exception:
            if data.get('username'):
                raise AuthenticationError('Invalid username or password')
            elif data.get('email'):
                raise AuthenticationError('Invalid email or password')
            else:
                raise AuthenticationError('Invalid credentials')

    def login_response(self, request, user):
        pass
