import time
import json

from datetime import datetime, timedelta

from pulsar import PermissionDenied, Http404
from pulsar.utils.pep import to_bytes, to_string
from pulsar.utils.importer import module_attribute

import lux
from lux import Router
from lux.forms import Form
from lux.utils.crypt import get_random_string, digest

from .jwtmixin import jwt
from .views import ForgotPassword
from .backend import REASON_BAD_TOKEN


__all__ = ['SessionMixin']


class SessionMixin(object):
    '''Mixin for :class:`.AuthBackend` via sessions.
    '''
    ForgotPasswordRouter = None
    dismiss_message = None

    def __init__(self, app):
        self._init(app)
        cfg = self.config
        self.session_cookie_name = cfg['SESSION_COOKIE_NAME']
        self.session_expiry = cfg['SESSION_EXPIRY']
        self.check_username = cfg['CHECK_USERNAME']
        self.csrf_expiry = cfg['CSRF_EXPIRY']
        self.jwt = jwt

    def wsgi(self):
        wsgi = [self]
        cfg = self.config
        if cfg['SESSION_MESSAGES']:
            wsgi.append(Router('_dismiss_message',
                               post=self._dismiss_message))
        return wsgi

    # ABSTRACT METHODS WHICH MUST BE IMPLEMENTED
    def get_session(self, key):
        '''Retrieve a session from its key
        '''
        raise NotImplementedError

    def session_key(self, session):
        '''Session key from session object
        '''
        raise NotImplementedError

    def session_save(self, session):
        raise NotImplementedError

    def session_create(self, request, user=None, expiry=None):
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

    def get_user_by_email(self, email):
        '''Get a user from its email address
        '''
        raise NotImplementedError

    def auth_key_used(self, key):
        '''The authentication ``key`` has been used and this method is
        for setting/updating the backend model accordingly.
        Used during password retrieval and user registration
        '''
        raise NotImplementedError

    # MIDDLEWARE
    def request(self, request):
        key = self.config['SESSION_COOKIE_NAME']
        session_key = request.cookies.get(key)
        session = None
        if session_key:
            session = self.get_session(session_key.value)
        if not session:
            session = self.session_create(request)
        request.cache.session = session
        if session.user:
            request.cache.user = session.user
        if not request.cache.user:
            request.cache.user = self.anonymous()

    def response(self, request, response):
        session = request.cache.session
        if session:
            if response.can_set_cookies():
                key = request.app.config['SESSION_COOKIE_NAME']
                session_key = request.cookies.get(key)
                id = self.session_key(session)
                if not session_key or session_key.value != id:
                    response.set_cookie(key, value=str(id), httponly=True,
                                        expires=session.expiry)

            self.session_save(session)
        return response

    # CSRF
    def csrf_token(self, request):
        session = request.cache.session
        if session:
            assert self.jwt, 'Requires jwt package'
            return self.jwt.encode({'session': self.session_key(session),
                                    'exp': time.time() + self.csrf_expiry},
                                   self.secret_key)

    def validate_csrf_token(self, request, token):
        if not token:
            raise PermissionDenied(REASON_BAD_TOKEN)
        try:
            assert self.jwt, 'Requires jwt package'
            token = self.jwt.decode(token, self.secret_key)
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
        user = self.get_user_by_email(email)
        if not self.get_or_create_registration(
                request, user,
                email_subject='password_email_subject.txt',
                email_message='password_email.txt',
                message='password_message.txt'):
            raise AuthenticationError("Can't find that email, sorry")

    def login(self, request, user=None):
        '''Login a user from a model or from post data
        '''
        if user is None:
            data = request.body_data()
            user = self.authenticate(request, **data)
            if user is None:
                raise AuthenticationError('Invalid username or password')
        if not user.is_active():
            return self.inactive_user_login(request, user)
        request.cache.session = self.session_create(request, user)
        request.cache.user = user
        return user

    def inactive_user_login(self, request, user):
        '''Handle a user not yet active'''
        cfg = request.config
        url = '%s/confirmation/%s' % (cfg['REGISTER_URL'], user.username)
        session = request.cache.session
        context = {'email': user.email,
                   'email_from': cfg['DEFAULT_FROM_EMAIL'],
                   'confirmation_url': url}
        message = request.app.render_template('inactive.txt', context)
        session.warning(message)

    def logout(self, request, user=None):
        '''Logout a ``user``
        '''
        session = request.cache.session
        user = user or request.cache.user
        if user and user.is_authenticated():
            request.cache.session = self.session_create(request)
            request.cache.user = self.anonymous()

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

    # INTERNALS
    def _dismiss_message(self, request):
        response = request.response
        if response.content_type in lux.JSON_CONTENT_TYPES:
            session = request.cache.session
            form = Form(request, data=request.body_data())
            data = form.rawdata['message']
            body = {'success': session.remove_message(data)}
            response.content = json.dumps(body)
            return response
