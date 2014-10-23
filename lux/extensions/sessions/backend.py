'''
.. autoclass:: AuthBackend
   :members:
   :member-order: bysource

'''
import time

from importlib import import_module
from datetime import datetime, timedelta

from pulsar import PermissionDenied, Http404
from pulsar.utils.pep import to_bytes, to_string
from pulsar.utils.importer import module_attribute

import lux
from lux import Parameter, Router
from lux.utils.crypt import get_random_string, digest

from .jwtmixin import jwt


__all__ = ['AuthBackend', 'SessionMixin', 'AuthenticationError',
           'LoginError', 'LogoutError', 'MessageMixin', 'UserMixin',
           'Anonymous', 'REASON_NO_REFERER', 'REASON_BAD_REFERER',
           'REASON_BAD_TOKEN']


UNUSABLE_PASSWORD = '!'
REASON_NO_REFERER = "Referer checking failed - no Referer"
REASON_BAD_REFERER = "Referer checking failed - %s does not match %s"
REASON_BAD_TOKEN = "CSRF token missing or incorrect"


class AuthenticationError(ValueError):
    pass


class LoginError(RuntimeError):
    pass


class LogoutError(RuntimeError):
    pass


class MessageMixin(object):
    '''Mixin for a messages
    '''
    def success(self, message):
        '''Store a ``success`` message to show to the web user
        '''
        self.message('success', message)

    def info(self, message):
        '''Store an ``info`` message to show to the web user
        '''
        self.message('info', message)

    def warning(self, message):
        '''Store a ``warning`` message to show to the web user
        '''
        self.message('warning', message)

    def error(self, message):
        '''Store an ``error`` message to show to the web user
        '''
        self.message('danger', message)

    def message(self, level, message):
        '''Store a ``message`` of ``level`` to show to the web user.

        Must be implemented by session classes.
        '''
        raise NotImplementedError

    def remove_message(self, data):
        '''Remove a message from the list of messages'''
        raise NotImplementedError


class UserMixin(object):
    '''Mixin for a User model
    '''
    email = None

    def is_superuser(self):
        return False

    def is_authenticated(self):
        return True

    def is_active(self):
        return False

    def is_anonymous(self):
        return False

    def get_id(self):
        raise NotImplementedError

    def get_oauths(self):
        '''Return a dictionary of oauths account'''
        return {}

    def set_oauth(self, name, data):
        raise NotImplementedError

    def remove_oauth(self, name):
        '''Remove a connected oauth account.
        Return ``True`` if successfully removed
        '''
        raise NotImplementedError

    def email_user(self, subject, message, from_email, **kwargs):
        '''Sends an email to this User'''
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @classmethod
    def get_by_username(cls, username):
        '''Retrieve a user from username
        '''
        raise NotImplementedError

    @classmethod
    def get_by_email(cls, email):
        raise NotImplementedError

    @classmethod
    def get_by_oauth(cls, name, identifier):
        '''Retrieve a user from OAuth ``name`` with ``identifier``
        '''
        raise NotImplementedError


class Anonymous(UserMixin):

    def is_authenticated(self):
        return False

    def is_anonymous(self):
        return True

    def get_id(self):
        return 0


class AuthBackend(object):
    '''Interface for authentication backends.

    An Authentication backend manage authentication, login, logout and
    several other activities which are required for managing users of
    a web site.
    '''
    def __init__(self, app):
        self.app = app

    @property
    def config(self):
        return self.app.config

    def __call__(self, environ, start_response):
        request = self.app.wsgi_request(environ)
        # Inject self as the authentication backend
        request.cache.auth_backend = self
        return self.request(request)

    def response_middleware(self, environ, response):
        request = self.app.wsgi_request(environ)
        # Inject self as the authentication backend
        request.cache.auth_backend = self
        return self.response(request, response)

    def request(self, request):
        '''Handle an incoming request'''
        pass

    def response(self, request, response):
        '''Handle an incoming ``response`` from a ``request``'''
        pass

    def get_user(self, request, **kwargs):
        '''Retrieve a user.
        Return ``None`` if the user could not be found'''
        pass

    def csrf_token(self, request):
        '''Create a CSRF token for a given request'''
        pass

    def validate_csrf_token(self, request, token):
        '''Validate CSRF
        '''
        pass

    def anonymous(self):
        '''An anonymous user'''
        return Anonymous()

    def create_user(self, request, **kwargs):
        '''Create a standard user.'''
        pass

    def create_superuser(self, request, *args, **kwargs):
        '''Create a user with *superuser* permissions.'''
        pass

    def has_permission(self, request, level, model):
        '''Check for permission on a model.'''
        return False

    def password(self, raw_password=None):
        if raw_password:
            return self._encript(raw_password)
        else:
            return UNUSABLE_PASSWORD

    def set_password(self, user, password):
        '''Set the password for ``user``.
        This method should commit changes.'''
        pass

    def normalise_email(self, email):
        """
        Normalise the address by lowercasing the domain part of the email
        address.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])
        return email

    def authenticate(self, request, **params):
        '''Authenticate user'''
        raise NotImplementedError


class SessionMixin(object):
    '''Mixin for authentication via sessions.

    An Authentication backend manage authentication, login, logout and
    several other activities which are required for managing users of
    a web site.
    '''
    model = None
    READ = 10
    UPDATE = 20
    CREATE = 30
    REMOVE = 40

    def __init__(self, app):
        self.app = app
        cfg = self.config
        self.encoding = cfg['ENCODING']
        self.secret_key = cfg['SECRET_KEY'].encode()
        self.session_cookie_name = cfg['SESSION_COOKIE_NAME']
        self.session_expiry = cfg['SESSION_EXPIRY']
        self.salt_size = cfg['AUTH_SALT_SIZE']
        self.check_username = cfg['CHECK_USERNAME']
        self.csrf_expiry = cfg['CSRF_EXPIRY']
        algorithm = cfg['CRYPT_ALGORITHM']
        self.crypt_module = import_module(algorithm)
        self.jwt = jwt
        #
        if cfg['SESSION_MESSAGES']:
            middleware.append(Router('_dismiss_message',
                                post=self._dismiss_message))
            reset = app.config['RESET_PASSWORD_URL']
            if reset:
                router = backend.ForgotPasswordRouter or ForgotPassword
                middleware.append(router(reset))

    def request(self, request):
        key = self.config['SESSION_COOKIE_NAME']
        session_key = request.cookies.get(key)
        session = None
        if session_key:
            session = self.get_session(session_key.value)
        if not session:
            session = self.create_session(request)
        request.cache.session = session
        if session.user:
            request.cache.user = session.user.get()
        if not request.cache.user:
            request.cache.user = self.anonymous()

    def response(self, request, response):
        session = request.cache.session
        if session:
            if response.can_set_cookies():
                key = request.app.config['SESSION_COOKIE_NAME']
                session_key = request.cookies.get(key)
                id = str(session.key.id())
                if not session_key or session_key.value != id:
                    response.set_cookie(key, value=str(id), httponly=True,
                                        expires=session.expiry)

            session.put()
        return response

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

    def create_session_id(self):
        while True:
            session_key = get_random_string(32)
            if not self.get_session(session_key):
                break
        return session_key

    def get_session(self, key):
        '''Retrieve a session from its key
        '''
        raise NotImplementedError

    def session_key(self, session):
        '''Session key from session object
        '''
        raise NotImplementedError

    def create_registration(self, request, user, expiry):
        '''Create a registration entry for a user.
        This method should return the registration/activation key.'''
        raise NotImplementedError

    def confirm_registration(self, request, **params):
        '''Confirm registration'''
        raise NotImplementedError

    def create_session(self, request, user=None, expiry=None):
        '''Create a new session
        '''
        raise NotImplementedError

    def auth_key_used(self, key):
        '''The authentication ``key`` has been used and this method is
        for setting/updating the backend model accordingly.
        Used during password retrieval and user registration
        '''
        raise NotImplementedError

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
        request.cache.session = self.create_session(request, user)
        request.cache.user = user
        return user

    def inactive_user_login(self, request, user):
        '''Handle a user not yet active'''
        cfg = request.config
        url = '/signup/confirmation/%s' % user.username
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
            request.cache.session = self.create_session(request)
            request.cache.user = Anonymous()

    def get_or_create_registration(self, request, user, **kw):
        '''Create a registration profile for ``user``.

        This method send an email to the user so that the email
        is verified once the user follows the link in the email.

        Usually called after user registration.
        '''
        if user and user.email:
            days = request.config['ACCOUNT_ACTIVATION_DAYS']
            expiry = datetime.now() + timedelta(days=days)
            auth_key = self.create_registration(request, user, expiry)
            self.send_email_confirmation(request, user, auth_key, **kw)
            return auth_key

    def password_recovery(self, request, email):
        user = self.model.get_by_email(email)
        if not self.get_or_create_registration(
                request, user, email_subject='password_email_subject.txt',
                email_message='password_email.txt',
                message='password_message.txt'):
            raise AuthenticationError("Can't find that email, sorry")

    def send_email_confirmation(self, request, user, auth_key,
                                email_subject=None, email_message=None,
                                message=None):
        '''Send an email to user to confirm his/her email address'''
        app = request.app
        cfg = app.config
        ctx = {'auth_key': auth_key,
               'expiration_days': cfg['ACCOUNT_ACTIVATION_DAYS'],
               'email': user.email,
               'site_uri': request.absolute_uri('/')[:-1]}

        subject = app.render_template(
            email_subject or 'activation_email_subject.txt', ctx)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = app.render_template(
            email_message or 'activation_email.txt', ctx)
        user.email_user(subject, body, cfg['DEFAULT_FROM_EMAIL'])
        message = app.render_template(
            message or 'activation_message.txt', ctx)
        request.cache.session.info(message)

    def decript(self, password=None):
        if password:
            p = self.crypt_module.decrypt(to_bytes(password, self.encoding),
                                          self.secret_key)
            return to_string(p, self.encoding)
        else:
            return UNUSABLE_PASSWORD

    # INTERNALS
    def _encript(self, password):
        p = self.crypt_module.encrypt(to_bytes(password, self.encoding),
                                      self.secret_key, self.salt_size)
        return to_string(p, self.encoding)
