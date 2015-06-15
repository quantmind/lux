import time

from datetime import datetime, timedelta

from pulsar import PermissionDenied, ImproperlyConfigured
from pulsar.apps.wsgi import Json

from lux import Parameter, wsgi_request

from .token import jwt, Authorization, AuthBackend
from ..user import AuthenticationError


REASON_BAD_TOKEN = "CSRF token missing or incorrect"
CSRF_SET = frozenset(('GET', 'HEAD', 'OPTIONS'))


class SessionBackend(AuthBackend):
    '''Mixin for :class:`.AuthBackend` via sessions.
    '''
    _config = [
        Parameter('SESSION_COOKIE_NAME', 'LUX',
                  'Name of the cookie which stores session id'),
        Parameter('CSRF_EXPIRY', 60*60,
                  'Cross Site Request Forgery token expiry in seconds.'),
        Parameter('CSRF_PARAM', 'authenticity_token',
                  'CSRF parameter name in forms')
    ]

    ForgotPasswordRouter = None
    dismiss_message = None

    def on_config(self, app):
        if not jwt:     # pragma    nocover
            raise ImproperlyConfigured('JWT library not available')

    def on_form(self, app, form):
        '''Handle CSRF on form
        '''
        request = form.request
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
                doc.head.add_meta(name="csrf-param", content=param)
                doc.head.add_meta(name="csrf-token", content=csrf_token)

    def api_sections(self, app):
        '''At the authorization router to the api
        '''
        yield Authorization()

    # MIDDLEWARE
    def request(self, request):
        key = request.config['SESSION_COOKIE_NAME']
        session_key = request.cookies.get(key)
        session = None
        if session_key:
            session = self.get_session(request, session_key.value)
        if not session:
            expiry = self.session_expiry(request)
            session = self.session_create(request, expiry=expiry)
        request.cache.session = session
        if session.user:
            request.cache.user = session.user
        if not request.cache.user:
            request.cache.user = self.anonymous()

    def response(self, environ, response):
        request = wsgi_request(environ)
        session = request.cache.session
        if session:
            if response.can_set_cookies():
                key = request.app.config['SESSION_COOKIE_NAME']
                session_key = request.cookies.get(key)
                id = self.session_key(session)
                if not session_key or session_key.value != id:
                    response.set_cookie(key, value=str(id), httponly=True,
                                        expires=session.expiry)

            self.session_save(request, session)
        return response

    def response_middleware(self, app):
        return [self.response]

    def login_response(self, request, user):
        '''Login response
        '''
        request.cache.session = self.session_create(request, user=user)
        request.cache.user = user
        return Json({'success': True,
                     'message': 'user login'}).http_response(request)

    def logout_response(self, request, user):
        if user.is_authenticated():
            request.cache.session = self.session_create(request)
            request.cache.user = self.anonymous()
        return Json({'authenticated': False}).http_response(request)

    # ABSTRACT METHODS WHICH MUST BE IMPLEMENTED
    def get_session(self, request, key):
        '''Retrieve a session from its key
        '''
        raise NotImplementedError

    def session_key(self, session):
        '''Session key from session object
        '''
        raise NotImplementedError

    def session_save(self, request, session):
        raise NotImplementedError

    def session_create(self, request, **kw):
        '''Create a new session
        '''
        raise NotImplementedError

    def create_registration(self, request, user, expiry):
        '''Create a registration entry for a user.
        This method should return the registration/activation key.'''
        raise NotImplementedError

    def confirm_registration(self, request, **params):
        '''Confirm registration'''
        raise NotImplementedError

    def auth_key_used(self, key):
        '''The authentication ``key`` has been used and this method is
        for setting/updating the backend model accordingly.
        Used during password retrieval and user registration
        '''
        raise NotImplementedError

    # CSRF
    def csrf_token(self, request):
        session = request.cache.session
        if session:
            expiry = request.config['CSRF_EXPIRY']
            secret_key = request.config['SECRET_KEY']
            return jwt.encode({'session': self.session_key(session),
                               'exp': time.time() + expiry},
                              secret_key)

    def validate_csrf_token(self, request, token):
        if not token:
            raise PermissionDenied(REASON_BAD_TOKEN)
        try:
            secret_key = request.config['SECRET_KEY']
            token = jwt.decode(token, secret_key)
        except jwt.ExpiredSignature:
            raise PermissionDenied('Expired token')
        except Exception:
            raise PermissionDenied(REASON_BAD_TOKEN)
        else:
            if token['session'] != self.session_key(request.cache.session):
                raise PermissionDenied(REASON_BAD_TOKEN)

    def password_recovery(self, request, email):
        '''Recovery password email
        '''
        user = self.get_user(email=email)
        if not self.get_or_create_registration(
                request, user,
                email_subject='password_email_subject.txt',
                email_message='password_email.txt',
                message='password_message.txt'):
            raise AuthenticationError("Can't find that email, sorry")

    def inactive_user_login_response(self, request, user):
        '''Handle a user not yet active'''
        cfg = request.config
        url = '%s/confirmation/%s' % (cfg['REGISTER_URL'], user.username)
        session = request.cache.session
        context = {'email': user.email,
                   'email_from': cfg['DEFAULT_FROM_EMAIL'],
                   'confirmation_url': url}
        message = request.app.render_template('inactive.txt', context)
        session.warning(message)

    def get_or_create_registration(self, request, user, **kw):
        '''Create a registration profile for ``user``.

        This method send an email to the user so that the email
        is verified once the user follows the link in the email.

        Usually called after user registration or password recovery.
        '''
        if user and user.email:
            days = request.config['ACCOUNT_ACTIVATION_DAYS']
            expiry = datetime.now() + timedelta(days=days)
            auth_key = self.create_registration(request, user, expiry)
            self.send_email_confirmation(request, user, auth_key, **kw)
            return auth_key

    def send_email_confirmation(self, request, user, auth_key, ctx=None,
                                email_subject=None, email_message=None,
                                message=None):
        '''Send an email to user to confirm his/her email address'''
        app = request.app
        cfg = app.config
        ctx = {'auth_key': auth_key,
               'register_url': cfg['REGISTER_URL'],
               'reset_password_url': cfg['RESET_PASSWORD_URL'],
               'expiration_days': cfg['ACCOUNT_ACTIVATION_DAYS'],
               'email': user.email,
               'site_uri': request.absolute_uri('/')[:-1]}

        subject = app.render_template(
            email_subject or 'activation_email_subject.txt', ctx)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = app.render_template(
            email_message or 'activation_email.txt', ctx)
        user.email_user(app, subject, body)
        message = app.render_template(
            message or 'activation_message.txt', ctx)
        request.cache.session.info(message)
