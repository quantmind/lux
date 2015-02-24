import time

from importlib import import_module
from datetime import datetime, timedelta

from pulsar import PermissionDenied, Http404
from pulsar.utils.pep import to_bytes, to_string
from pulsar.utils.importer import module_attribute
from pulsar.apps.wsgi import WsgiHandler

import lux
from lux.utils.crypt import get_random_string, digest


__all__ = ['AuthBackend', 'AuthenticationError',
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
    '''Mixin for models which support messages
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

    def get_messages(self):
        '''Retrieve messages
        '''
        return ()


class UserMixin(MessageMixin):
    '''Mixin for a User model
    '''
    email = None

    def is_superuser(self):
        return False

    def is_authenticated(self):
        '''Return ``True`` if the user is is_authenticated
        '''
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

    def todict(self):
        '''Return a dictionary with information about the user'''

    def email_user(self, app, subject, body, sender=None):
        backend = app.email_backend
        backend.send_mail(app, sender, self.email, subject, body)

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

    An authentication backend manage authentication, login, logout and
    several other activities which are required for managing users of
    a web site.

    During a client ``request``, the instance of the authentication backend
    can be accessed from the ``request`` cache dictionary::

        backend = request.cache.auth_backend
    '''
    CREATE = 30     # C
    READ = 10       # R
    UPDATE = 20     # U
    DELETE = 40     # D

    def _init(self, app):
        self.app = app
        cfg = app.config
        self.encoding = cfg['ENCODING']
        self.secret_key = cfg['SECRET_KEY'].encode()
        self.salt_size = cfg['AUTH_SALT_SIZE']
        algorithm = cfg['CRYPT_ALGORITHM']
        self.crypt_module = import_module(algorithm)

    @property
    def config(self):
        return self.app.config

    def __call__(self, environ, start_response):
        request = self.app.wsgi_request(environ)
        # Inject self as the authentication backend
        request.cache.auth_backend = self
        return self.request(request)

    def wsgi(self):
        return [self]

    def response_middleware(self, environ, response):
        request = self.app.wsgi_request(environ)
        return self.response(request, response)

    def request(self, request):
        '''Handle an incoming request and should be implemented.'''
        pass

    def response(self, request, response):
        '''Handle an outgoing ``response`` from a ``request``.
        By default it returns ``response`` without performing any operations.
        '''
        return response

    def get_user(self, request, **kwargs):
        '''Retrieve a user.
        Return ``None`` if the user could not be found'''
        pass

    def csrf_token(self, request):
        '''Create a CSRF token for a given request.'''
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
            return self.encript(raw_password)
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

    def logout(self, request, user=None):
        ''''Logout a user'''
        raise NotImplementedError

    def decript(self, password=None):
        if password:
            p = self.crypt_module.decrypt(to_bytes(password, self.encoding),
                                          self.secret_key)
            return to_string(p, self.encoding)
        else:
            return UNUSABLE_PASSWORD

    def encript(self, password):
        p = self.crypt_module.encrypt(to_bytes(password, self.encoding),
                                      self.secret_key, self.salt_size)
        return to_string(p, self.encoding)
