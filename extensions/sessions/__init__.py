import time

from pulsar import PermissionDenied

import jwt

from lux.core import Parameter, LuxExtension, is_html

from .browser import SessionBackend
from .views import Login, Logout, SignUp, ForgotPassword, Token


__all__ = ['SessionBackend']


CSRF_SET = frozenset(('GET', 'HEAD', 'OPTIONS'))


class Extension(LuxExtension):
    """Extension for persistent sessions between server and web browsers

    Add CSRF to forms
    """
    _config = [
        #
        # SESSIONS
        Parameter('SESSION_COOKIE_NAME', 'LUX',
                  'Name of the cookie which stores session id'),
        Parameter('SESSION_EXCLUDE_URLS', (),
                  'Tuple of urls where persistent session is not required'),
        Parameter('SESSION_EXPIRY', 7 * 24 * 60 * 60,
                  'Expiry for a session/token in seconds.'),
        Parameter('SESSION_STORE', None,
                  'Cache backend for session objects.'),
        Parameter('APP_JWT', None,
                  'Application JWT'),
        #
        # CSRF
        Parameter('CSRF_EXPIRY', 60 * 60,
                  'Cross Site Request Forgery token expiry in seconds'),
        Parameter('CSRF_PARAM', 'authenticity_token',
                  'CSRF parameter name in forms, set to None to skip CSRF '
                  '(not recommended)'),
        Parameter('CSRF_BAD_TOKEN_MESSAGE', 'CSRF token missing or incorrect',
                  'Message to display when CSRF is wrong'),
        Parameter('CSRF_EXPIRED_TOKEN_MESSAGE', 'CSRF token expired',
                  'Message to display when CSRF token has expired'),
        #
        Parameter('POST_LOGIN_URL', '',
                  'URL users are redirected to after logging in', True),
        Parameter('POST_LOGOUT_URL', None,
                  'URL users are redirected to after logged out', True),
        Parameter('LOGIN_URL', '/login', 'Url to login page', True),
        Parameter('LOGOUT_URL', '/logout', 'Url to logout', True),
        Parameter('HTML_AUTH_TOKEN_URL', '/token',
                  'URL for retrieving the authorization token'),
        Parameter('REGISTER_URL', '/signup',
                  'Url to register with site', True),
        Parameter('TOS_URL', '/tos',
                  'Terms of Service url',
                  True),
        Parameter('PRIVACY_POLICY_URL', '/privacy-policy',
                  'The url for the privacy policy, required for signups',
                  True),
        Parameter('REGISTER_URL', '/signup',
                  'Url to register with site', True),
        Parameter('RESET_PASSWORD_URL', '/reset-password',
                  'If given, add the router to handle password resets',
                  True)
    ]

    def middleware(self, app):
        if is_html(app):
            cfg = app.config

            if cfg['LOGIN_URL']:
                yield Login(cfg['LOGIN_URL'])
                if cfg['LOGOUT_URL']:
                    yield Logout(cfg['LOGOUT_URL'])
                if cfg['HTML_AUTH_TOKEN_URL']:
                    yield Token(cfg['HTML_AUTH_TOKEN_URL'])

            if cfg['REGISTER_URL']:
                yield SignUp(cfg['REGISTER_URL'])

            if cfg['RESET_PASSWORD_URL']:
                yield ForgotPassword(cfg['RESET_PASSWORD_URL'])

    def on_jwt(self, app, request, payload):
        cfg = app.config
        if cfg['REGISTER_URL']:
            payload['registration_url'] = request.absolute_uri(
                cfg['REGISTER_URL'])
        if cfg['RESET_PASSWORD_URL']:
            payload['password_reset_url'] = request.absolute_uri(
                cfg['RESET_PASSWORD_URL'])

    def on_form(self, app, form):
        """Handle CSRF on form
        """
        request = form.request
        if request.cache.skip_session_backend:
            return
        param = app.config['CSRF_PARAM']
        if (param and form.is_bound and
                request.method not in CSRF_SET):
            token = form.rawdata.get(param)
            self.validate_csrf_token(request, token)

    def on_html_document(self, app, request, doc):
        if request.method in CSRF_SET:
            cfg = app.config
            param = cfg['CSRF_PARAM']
            if param:
                csrf_token = self.csrf_token(request)
                if csrf_token:
                    doc.head.add_meta(name="csrf-param", content=param)
                    doc.head.add_meta(name="csrf-token", content=csrf_token)

    def context(self, request, context):
        """Add user to the Html template context"""
        context['user'] = request.cache.user

    # CSRF
    def csrf_token(self, request):
        session = request.cache.session
        if session:
            expiry = request.config['CSRF_EXPIRY']
            return jwt.encode({'exp': time.time() + expiry}, session.id)

    def validate_csrf_token(self, request, token):
        bad_token = request.config['CSRF_BAD_TOKEN_MESSAGE']
        expired_token = request.config['CSRF_EXPIRED_TOKEN_MESSAGE']
        if not token:
            raise PermissionDenied(bad_token)
        try:
            jwt.decode(token, request.cache.session.id)
        except jwt.ExpiredSignature:
            raise PermissionDenied(expired_token)
        except Exception:
            raise PermissionDenied(bad_token)
