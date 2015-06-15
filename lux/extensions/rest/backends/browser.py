from pulsar.utils.httpurl import is_absolute_uri

from lux import Parameter
from lux.extensions.angular import add_ng_modules

from .. import AuthBackend, luxrest
from ..views import Login, SignUp, ForgotPassword


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

    def middleware(self, app):
        middleware = []
        cfg = app.config
        api = cfg['API_URL']

        if cfg['LOGIN_URL']:
            action = luxrest(api, 'authorizations_url')
            middleware.append(Login(cfg['LOGIN_URL'], form_action=action))

        if cfg['REGISTER_URL']:
            middleware.append(SignUp(cfg['REGISTER_URL']))

        if cfg['RESET_PASSWORD_URL']:
            middleware.append(ForgotPassword(cfg['RESET_PASSWORD_URL']))

        return middleware

    def on_html_document(self, app, request, doc):
        if is_absolute_uri(app.config['API_URL']):
            add_ng_modules(doc, ('lux.restapi', 'lux.users'))
        else:
            add_ng_modules(doc, ('lux.webapi', 'lux.users'))
