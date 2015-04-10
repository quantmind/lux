from lux import Parameter

from pulsar.utils.httpurl import is_absolute_uri

from .. import AuthBackend, luxrest
from ..views import Login, Logout, SignUp, ForgotPassword


class BrowserBackend(AuthBackend):
    '''Authentication backend for rendering Forms

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

    def middleware(self, app):
        middleware = []
        cfg = app.config
        api_url = cfg['API_URL']

        # If the API_URL is absolute, pass the luxrest api name for the
        # processForm
        if is_absolute_uri(api_url):
            if cfg['LOGIN_URL']:
                url = luxrest(api_url, 'authorizations')
                middleware.append(Login(cfg['LOGIN_URL'], post=url))

        else:
            if cfg['LOGIN_URL']:
                middleware.append(Login(cfg['LOGIN_URL']))
                middleware.append(Logout(cfg['LOGOUT_URL']))

        if cfg['REGISTER_URL']:
            middleware.append(SignUp(cfg['REGISTER_URL']))
        if cfg['RESET_PASSWORD_URL']:
            middleware.append(ForgotPassword(cfg['RESET_PASSWORD_URL']))
        return middleware
