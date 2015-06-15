import time

from pulsar import HttpException, ImproperlyConfigured
from pulsar.apps.wsgi import Json

try:
    import jwt
except ImportError:     # pragma    nocover
    jwt = None

from lux import Parameter

from ..views import Authorization
from .. import AuthBackend


class Http401(HttpException):

    def __init__(self, auth, msg=''):
        headers = [('WWW-Authenticate', auth)]
        super().__init__(msg=msg, status=401, headers=headers)


class TokenBackend(AuthBackend):
    '''Backend based on JWT_

    Once a ``jtw`` is created, authetication is achieved by setting
    the ``Authorization`` header to ``Bearer jwt``.

    Requires pyjwt_ package.

    .. _pyjwt: https://pypi.python.org/pypi/PyJWT
    .. _JWT: http://self-issued.info/docs/draft-ietf-oauth-json-web-token.html
    '''
    _config = [
        Parameter('CORS_ALLOWED_METHODS', 'GET, PUT, POST, DELETE, HEAD',
                  'Access-Control-Allow-Methods for CORS')
    ]

    def on_config(self, app):
        if not jwt:     # pragma    nocover
            raise ImproperlyConfigured('JWT library not available')

    def api_sections(self, app):
        '''At the authorization router to the api
        '''
        yield Authorization()

    def request(self, request):
        '''Check for ``HTTP_AUTHORIZATION`` header and if it is available
        and the authentication type if ``bearer`` try to perform
        authentication using JWT_.
        '''
        auth = request.get('HTTP_AUTHORIZATION')
        user = request.cache.user
        if auth and user.is_anonymous():
            auth_type, key = auth.split(None, 1)
            auth_type = auth_type.lower()
            if auth_type == 'bearer':
                try:
                    data = jwt.decode(key, self.secret_key)
                except jwt.ExpiredSignature:
                    request.app.logger.info('JWT token has expired')
                    # In this case we want the client to perform
                    # a new authentication. Raise 401
                    raise Http401('Token')
                except Exception:
                    request.app.logger.exception('Could not load user')
                else:
                    user = self.get_user(request, **data)
                    if user:
                        request.cache.user = user

    def response(self, environ, response):
        name = 'Access-Control-Allow-Origin'
        if name not in response.headers:
            origin = environ.get('HTTP_ORIGIN', '*')
            response[name] = origin
        return response

    def response_middleware(self, app):
        return [self.response]

    def login_response(self, request, user):
        token = self.create_token(request, user)
        token = token.decode('utf-8')
        request.response.status_code = 201
        return Json({'success': True,
                     'token': token}).http_response(request)

    def logout_response(self, request, user):
        return Json({'success': True,
                     'message': 'loged out'}).http_response(request)

    def on_preflight(self, app, request):
        '''Preflight handler
        '''
        headers = request.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
        methods = app.config['CORS_ALLOWED_METHODS']
        response = request.response
        origin = request.get('HTTP_ORIGIN', '*')

        if origin == 'null':
            origin = '*'

        response['Access-Control-Allow-Origin'] = origin
        if headers:
            response['Access-Control-Allow-Headers'] = headers
        response['Access-Control-Allow-Methods'] = methods

    def create_token(self, request, user, **kwargs):    # pragma    nocover
        '''Create the JWT
        '''
        raise NotImplementedError

    def jwt_payload(self, request, user):
        '''Add user-related payload to the JWT
        '''
        expiry = self.session_expiry(request)
        payload = {'user_id': user.id,
                   'superuser': user.is_superuser()}
        if expiry:
            payload['exp'] = int(time.mktime(expiry.timetuple()))
        return payload

    def encode_payload(self, request, payload):
        return jwt.encode(payload, request.config['SECRET_KEY'])
