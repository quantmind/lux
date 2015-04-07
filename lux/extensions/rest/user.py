import time

from importlib import import_module
from datetime import datetime, timedelta

from pulsar import PermissionDenied, Http404
from pulsar.utils.pep import to_bytes, to_string

import lux
from lux.utils.crypt import get_random_string, digest


__all__ = ['AuthBackend', 'AuthenticationError',
           'LoginError', 'LogoutError', 'MessageMixin', 'UserMixin',
           'Anonymous', 'CREATE', 'READ', 'UPDATE', 'DELETE']


UNUSABLE_PASSWORD = '!'

CREATE = 30     # C
READ = 10       # R
UPDATE = 20     # U
DELETE = 40     # D


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


class PasswordMixin:

    def on_config(self, app):
        cfg = app.config
        self.encoding = cfg['ENCODING']
        self.secret_key = cfg['SECRET_KEY'].encode()
        self.salt_size = cfg['AUTH_SALT_SIZE']
        algorithm = cfg['CRYPT_ALGORITHM']
        self.crypt_module = import_module(algorithm)

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

    def password(self, raw_password=None):
        if raw_password:
            return self.encript(raw_password)
        else:
            return UNUSABLE_PASSWORD

    def set_password(self, user, password):
        '''Set the password for ``user``.
        This method should commit changes.'''
        pass


def normalise_email(email):
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
