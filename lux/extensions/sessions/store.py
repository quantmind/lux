from pulsar import ImproperlyConfigured
from pulsar.utils.structures import AttributeDictionary

from lux.core import create_cache, app_attribute
from lux.utils.crypt import create_token


class SessionMixin:
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


class Session(AttributeDictionary, SessionMixin):
    '''A dictionary-based Session

    Used by the :class:`.ApiSessionBackend`
    '''
    def todict(self):
        return self.__dict__.copy()


class SessionStore:
    """Backend Interface for browser sessions
    """
    def __init__(self, store):
        self.store = store

    def get(self, id):
        """Get a session at id
        """
        obj = self.store.get_json(self.session_key(id))
        if obj:
            return Session(obj)

    def set(self, id, data):
        """Set session data at id
        """
        self.store.set_json(self.session_key(id), data)

    def delete(self, id):
        """Delete session at id
        """
        self.store.delete(self.session_key(id))

    def clear(self, app_name=None):
        """Clear all sessions for the application name
        """
        key = self.session_key(app_name=app_name)
        return self.store.clear(key)

    def create(self, id=None, **kw):
        id = id or create_token()
        return Session(id=id, **kw)

    def save(self, session):
        self.set(session.id, session.todict())

    def session_key(self, id=None, app_name=None):
        app_name = app_name or self.store.app.config['APP_NAME']
        base = 'session:%s:' % app_name
        return '%s:%s' % (base, id) if id else base


@app_attribute
def session_store(app):
    url = app.config['SESSION_STORE']
    if not url:
        raise ImproperlyConfigured('SESSION_STORE required by '
                                   'authentication backend')
    return SessionStore(create_cache(app, url))
