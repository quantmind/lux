from importlib import import_module

from pulsar.utils.structures import AttributeDictionary
from pulsar.utils.pep import to_bytes


UNUSABLE_PASSWORD = '!'


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

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        return self.__repr__()

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
        backend.send_mail(sender, self.email, subject, body)

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


class SessionMixin:
    '''Mixin for web sessions & tokens
    '''
    encoded = None
    '''Encoded representation of this session'''

    def get_user(self):
        return self.user

    def get_key(self):
        return self.id

    def __repr__(self):
        return self.get_key()
    __str__ = __repr__


class PasswordMixin:
    '''Adds password encryption to an authentication backend.

    It has two basic methods,
    :meth:`.encrypt` and :meth:`.decrypt`.
    '''
    def on_config(self, app):
        cfg = app.config
        self.encoding = cfg['ENCODING']
        self.secret_key = cfg['PASSWORD_SECRET_KEY'].encode()
        ckwargs = cfg['CRYPT_ALGORITHM']
        if not isinstance(ckwargs, dict):
            ckwargs = dict(module=ckwargs)
        self.ckwargs = ckwargs.copy()
        self.crypt_module = import_module(self.ckwargs.pop('module'))

    def encrypt(self, string_or_bytes):
        '''Encrypt ``string_or_bytes`` using the algorithm specified
        in the :setting:`CRYPT_ALGORITHM` setting.

        Return an encrypted string
        '''
        b = to_bytes(string_or_bytes, self.encoding)
        p = self.crypt_module.encrypt(b, self.secret_key, **self.ckwargs)
        return p.decode(self.encoding)

    def crypt_verify(self, encrypted, raw):
        '''Verify if the ``raw`` string match the ``encrypted`` string
        '''
        return self.crypt_module.verify(to_bytes(encrypted),
                                        to_bytes(raw),
                                        self.secret_key,
                                        **self.ckwargs)

    def decrypt(self, string_or_bytes):
        b = to_bytes(string_or_bytes, self.encoding)
        p = self.crypt_module.decrypt(b, self.secret_key)
        return p.decode(self.encoding)

    def password(self, raw_password=None):
        '''Return an encrypted password
        '''
        if raw_password:
            return self.encrypt(raw_password)
        else:
            return UNUSABLE_PASSWORD


class User(AttributeDictionary, UserMixin):
    '''A dictionary-based user

    Used by the :class:`.ApiSessionBackend`
    '''
    def is_superuser(self):
        return self.superuser

    def is_active(self):
        return True

    def __str__(self):
        return self.username or self.email or 'user'


class Session(AttributeDictionary, SessionMixin):
    '''A dictionary-based Session

    Used by the :class:`.ApiSessionBackend`
    '''
    pass
