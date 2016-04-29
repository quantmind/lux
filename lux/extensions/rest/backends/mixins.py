import time
from functools import wraps
from datetime import datetime, timedelta

from pulsar import ImproperlyConfigured, Http401
from pulsar.utils.pep import to_string
from pulsar.apps.wsgi import Route, wsgi_request

from lux.core import app_attribute

try:
    import jwt
except ImportError:     # pragma    nocover
    jwt = None


class TokenBackendMixin:
    """Mixin for token and session based authentication back-ends
    """
    def session_expiry(self, request):
        """Expiry for a session or a token
        """
        session_expiry = request.config['SESSION_EXPIRY']
        if session_expiry:
            return datetime.now() + timedelta(seconds=session_expiry)

    def encode_token(self, request, user=None, expiry=None, **token):
        """Encode a JWT
        """
        if not jwt:     # pragma    nocover
            raise ImproperlyConfigured('JWT library not available')

        if expiry:
            token['exp'] = int(time.mktime(expiry.timetuple()))

        request.app.fire('on_token', request, token, user)
        return to_string(jwt.encode(token, request.config['SECRET_KEY']))

    def decode_token(self, request, token):
        if not jwt:     # pragma    nocover
            raise ImproperlyConfigured('JWT library not available')
        try:
            return jwt.decode(token, request.config['SECRET_KEY'])
        except jwt.ExpiredSignature:
            request.app.logger.warning('JWT token has expired')
            raise Http401('Token')
        except jwt.DecodeError as exc:
            request.app.logger.warning(str(exc))
            raise Http401('Token')

    def create_token(self, request, user, **kwargs):  # pragma    nocover
        """Create a new token and store it
        """
        raise NotImplementedError


@app_attribute
def exclude_urls(app):
    urls = []
    for url in app.config['SESSION_EXCLUDE_URLS']:
        urls.append(Route(url))
    return tuple(urls)


def skip_on_exclude(method):

    @wraps(method)
    def _(self, request, *args):
        path = request.path[1:]
        for url in exclude_urls(request.app):
            if url.match(path):
                return

        return method(self, request, *args)

    return _


class SessionBackendMixin(TokenBackendMixin):
    """Mixin for :class:`.AuthBackend` via sessions.

    This mixin implements the request and response middleware and introduce
    three abstract method for session CRUD operations.
    """
    def logout(self, request):
        request.cache.user = self.anonymous()
        request.cache.session = self.create_session(request)

    @skip_on_exclude
    def login(self, request, user):
        session = self.create_session(request, user)
        request.cache.session = session
        token = session.encoded
        request.response.status_code = 201
        return {'success': True,
                'token': token}

    def on_html_document(self, app, request, doc):
        """Add the user-token meta tag
        """
        if request.method == 'GET':
            session = request.cache.session
            if session and session.user:
                doc.head.add_meta(name="user-token", content=session.encoded)

    # MIDDLEWARE
    @skip_on_exclude
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
        return self._response_session(wsgi_request(environ), response)

    @skip_on_exclude
    def _response_session(self, request, response):
        session = request.cache.session
        if session:
            if response.can_set_cookies():
                key = request.config['SESSION_COOKIE_NAME']
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
        """Retrieve a session from its key
        """
        raise NotImplementedError

    def create_session(self, request, user=None):
        """Create a new session
        """
        raise NotImplementedError

    def session_save(self, request, session):
        """Save an existing session
        """
        raise NotImplementedError
