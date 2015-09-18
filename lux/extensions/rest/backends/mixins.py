import time

from pulsar import HttpException, ImproperlyConfigured
from pulsar.utils.pep import to_string
from pulsar.apps.wsgi import Json

from lux import Parameter, wsgi_request, Http401

from ..views import Authorization

try:
    import jwt
except ImportError:     # pragma    nocover
    jwt = None


class TokenBackendMixin:

    def api_sections(self, app):
        '''At the authorization router to the api
        '''
        yield Authorization()

    def encode_token(self, request, user=None, expiry=None, **token):
        '''Encode a JWT
        '''
        if not jwt:     # pragma    nocover
            raise ImproperlyConfigured('JWT library not available')

        if expiry:
            token['exp'] = int(time.mktime(expiry.timetuple()))
        request.app.fire('on_token', request, token, user)
        return jwt.encode(token, request.config['SECRET_KEY'])

    def decode_token(self, request, token):
        if not jwt:     # pragma    nocover
            raise ImproperlyConfigured('JWT library not available')
        try:
            return jwt.decode(token, request.config['SECRET_KEY'])
        except jwt.ExpiredSignature:
            request.app.logger.info('JWT token has expired')
            # In this case we want the client to perform
            # a new authentication. Raise 401
            raise Http401('Token')

    def create_token(self, request, user, **kwargs):  # pragma    nocover
        '''Create a new token and store it
        '''
        raise NotImplementedError


class SessionBackendMixin(TokenBackendMixin):
    '''Mixin for :class:`.AuthBackend` via sessions.

    This mixin implement the request and response middleware and introduce
    three abstract method for session CRUD operations
    '''
    _config = [
        Parameter('SESSION_COOKIE_NAME', 'LUX',
                  'Name of the cookie which stores session id')
    ]

    def login_response(self, request, user):
        session = self.create_session(request, user)
        request.cache.session = session
        token = to_string(session.encoded)
        request.response.status_code = 201
        return Json({'success': True,
                     'token': token}).http_response(request)

    def logout_response(self, request, user):
        '''Logout and create a new session
        '''
        if user.is_authenticated():
            request.cache.user = self.anonymous()
            request.cache.session = self.create_session(request)
        return Json({'success': True}).http_response(request)

    # MIDDLEWARE
    def request(self, request):
        key = request.config['SESSION_COOKIE_NAME']
        session_key = request.cookies.get(key)
        session = None
        if session_key:
            session = self.get_session(request, session_key.value)
        if not session:
            # Create an anonymous session
            session = self.create_session(request)
        request.cache.session = session
        user = session.get_user()
        if user:
            request.cache.user = user

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

    def create_session(self, request, user=None):
        '''Create a new session
        '''
        raise NotImplementedError

    def session_save(self, request, session):
        '''Save an existing session
        '''
        raise NotImplementedError
