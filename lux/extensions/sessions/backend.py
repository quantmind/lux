from importlib import import_module

from pulsar import PermissionDenied, Http404
from pulsar.utils.pep import to_bytes, to_string
from pulsar.utils.importer import module_attribute

import lux
from lux import Parameter
from lux.utils.crypt import get_random_string, digest


__all__ = ['AuthBackend', 'AuthenticationError', 'LoginError', 'LogoutError']


UNUSABLE_PASSWORD = '!'


class AuthenticationError(ValueError):
    pass


class LoginError(RuntimeError):
    pass


class LogoutError(RuntimeError):
    pass


class AuthBackend(object):
    '''Interface for authentication backends.

    An Authentication backend manage authentication, login, logout and
    several other activities which are required for managing users of
    a web site.
    '''
    model = None

    def __init__(self, app):
        self.encoding = app.config['ENCODING']
        self.secret_key = app.config['SECRET_KEY'].encode()
        self.session_cookie_name = app.config['SESSION_COOKIE_NAME']
        self.session_expiry = app.config['SESSION_EXPIRY']
        self.salt_size = app.config['AUTH_SALT_SIZE']
        self.csrf = app.config['CSRF_KEY_LENGTH']
        self.check_username = app.config['CHECK_USERNAME']
        algorithm = app.config['CRYPT_ALGORITHM']
        self.crypt_module = import_module(algorithm)

    def authenticate(self, request, user, **params):
        '''Authenticate a user'''
        pass

    def login(self, request, user=None):
        '''Login a ``user`` if it is already authenticated, otherwise do
        nothing.'''
        raise NotImplementedError

    def logout(self, request, user=None):
        '''Logout a ``user``
        '''
        session = request.cache.session
        user = user or request.cache.user
        if user and user.is_authenticated():
            request.cache.session = self.create_session(request)
            request.cache.user = Anonymous()

    def get_user(self, request, *args, **kwargs):
        '''Retrieve a user.

        This method can raise an exception if the user could not be found,
        or return ``None``.
        '''
        pass

    def create_session(self, request, user=None, expiry=None):
        '''Create a new session
        '''
        raise NotImplementedError

    def create_user(self, request, **kwargs):
        '''Create a standard user.'''
        pass

    def create_superuser(self, request, *args, **kwargs):
        '''Create a user with *superuser* permissions.'''
        pass

    def middleware(self, app):
        return ()

    def response_middleware(self, app):
        return ()

    def has_permission(self, request, action, model):
        '''Check for permission on a model.'''
        pass

    def password(self, raw_password=None):
        if raw_password:
            return self._encript(raw_password)
        else:
            return UNUSABLE_PASSWORD

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

    def send_email_confirmation(self, request, user):
        '''Send an email to user to confirm his/her email address'''
        cache = request.cache_server
        app = request.app
        cfg = app.config
        activation_key = digest(user.username)
        ctx = {'activation_key': activation_key,
               'expiration_days': cfg['ACCOUNT_ACTIVATION_DAYS'],
               'site_uri': request.absolute_uri('/')[:-1]}
        subject = app.render_template('activation_email_subject.txt', ctx)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        message = app.render_template('activation_email.txt', ctx)
        user.email_user(subject, message, cfg['DEFAULT_FROM_EMAIL'])

    # INTERNALS
    def _encript(self, password):
        p = self.crypt_module.encrypt(to_bytes(password, self.encoding),
                                      self.secret_key, self.salt_size)
        return to_string(p, self.encoding)
