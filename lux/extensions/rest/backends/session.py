import time

from datetime import datetime, timedelta

from pulsar import PermissionDenied, ImproperlyConfigured

from lux import Parameter

from .token import jwt, Authorization, AuthBackend
from ..user import AuthenticationError
from .mixins import SessionBackendMixin


class SessionBackend(SessionBackendMixin, AuthBackend):

    def api_sections(self, app):
        '''At the authorization router to the api
        '''
        yield Authorization()

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


class CsrfBackend(AuthBackend):
    '''A backend for Cross-Site Request Forgery prevention.

    Can be used on a session backend.
    '''
    _config = [
        Parameter('CSRF_EXPIRY', 60*60,
                  'Cross Site Request Forgery token expiry in seconds.'),
        Parameter('CSRF_PARAM', 'authenticity_token',
                  'CSRF parameter name in forms')
    ]
    REASON_BAD_TOKEN = "CSRF token missing or incorrect"
    CSRF_SET = frozenset(('GET', 'HEAD', 'OPTIONS'))

    def on_form(self, app, form):
        '''Handle CSRF on form
        '''
        request = form.request
        param = app.config['CSRF_PARAM']
        if (param and form.is_bound and
                request.method not in self.CSRF_SET):
            token = form.rawdata.get(param)
            self.validate_csrf_token(request, token)

    def on_html_document(self, app, request, doc):
        if request.method in self.CSRF_SET:
            cfg = app.config
            param = cfg['CSRF_PARAM']
            if param:
                csrf_token = self.csrf_token(request)
                if csrf_token:
                    doc.head.add_meta(name="csrf-param", content=param)
                    doc.head.add_meta(name="csrf-token", content=csrf_token)

    # CSRF
    def csrf_token(self, request):
        if not jwt:     # pragma    nocover
            raise ImproperlyConfigured('JWT library not available')
        session = request.cache.session
        if session:
            expiry = request.config['CSRF_EXPIRY']
            secret_key = request.config['SECRET_KEY']
            return jwt.encode({'session': session.get_key(),
                               'exp': time.time() + expiry},
                              secret_key)

    def validate_csrf_token(self, request, token):
        if not jwt:     # pragma    nocover
            raise ImproperlyConfigured('JWT library not available')
        if not token:
            raise PermissionDenied(self.REASON_BAD_TOKEN)
        try:
            secret_key = request.config['SECRET_KEY']
            token = jwt.decode(token, secret_key)
        except jwt.ExpiredSignature:
            raise PermissionDenied('Expired token')
        except Exception:
            raise PermissionDenied(self.REASON_BAD_TOKEN)
        else:
            if token['session'] != request.cache.session.get_key():
                raise PermissionDenied(self.REASON_BAD_TOKEN)
