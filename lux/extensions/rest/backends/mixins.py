import uuid

from pulsar.utils.structures import AttributeDictionary
from pulsar.apps.wsgi import Json

from lux import Parameter, wsgi_request

from ..user import SessionMixin


class Session(AttributeDictionary, SessionMixin):
    pass


class SessionBackendMixin:
    '''Mixin for :class:`.AuthBackend` via sessions.
    '''
    _config = [
        Parameter('SESSION_COOKIE_NAME', 'LUX',
                  'Name of the cookie which stores session id')
    ]

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

    def response_session(self, environ, response):
        request = wsgi_request(environ)
        session = request.cache.session
        if session:
            if response.can_set_cookies():
                key = request.app.config['SESSION_COOKIE_NAME']
                session_key = request.cookies.get(key)
                id = session.get_key()
                if not session_key or session_key.value != id:
                    response.set_cookie(key, value=str(id), httponly=True,
                                        expires=session.expiry)

            self.session_save(request, session)
        return response

    def response_middleware(self, app):
        return [self.response_session]

    # ABSTRACT METHODS WHICH MUST BE IMPLEMENTED
    def get_session(self, request, key):
        '''Retrieve a session from its key
        '''
        raise NotImplementedError

    def session_save(self, request, session):
        raise NotImplementedError

    def session_create(self, request, **kw):
        '''Create a new session
        '''
        raise NotImplementedError


class CacheSessionMixin:
    '''A mixin for storing session in cache
    '''
    def get_session(self, request, key):
        session = request.app.cache_server.get_json(self._key(key))
        if session:
            session = Session(session)
            if session.user_id:
                session.user = self.get_user(request, user_id=session.user_id)
            return session

    def session_save(self, request, session):
        session = session.all().copy()
        session.pop('user', None)
        request.app.cache_server.set_json(self._key(session['id']), session)

    def session_create(self, request, id=None, user=None, expiry=None):
        '''Create a new session
        '''
        if not id:
            id = uuid.uuid4().hex
        session = Session(id=id)
        if expiry:
            session.expiry = expiry.isoformat()
        if user:
            session.user_id = user.id
            session.user = user
        return session

    def _key(self, id):
        return 'session:%s' % id
