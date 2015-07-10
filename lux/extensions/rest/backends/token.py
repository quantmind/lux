from pulsar import HttpException, ImproperlyConfigured
from pulsar.utils.pep import to_string
from pulsar.apps.wsgi import Json

from lux import Parameter

from .. import AuthBackend
from .mixins import jwt, TokenBackendMixin


class Http401(HttpException):

    def __init__(self, auth, msg=''):
        headers = [('WWW-Authenticate', auth)]
        super().__init__(msg=msg, status=401, headers=headers)


class TokenBackend(TokenBackendMixin, AuthBackend):
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

    def login_response(self, request, user):
        expiry = self.session_expiry(request)
        token = self.create_token(request, user, expiry=expiry)
        token = to_string(token.encoded)
        request.response.status_code = 201
        return Json({'success': True,
                     'token': token}).http_response(request)

    def logout_response(self, request, user):
        '''TODO: do we set the token as expired!? Or we simply do nothing?
        '''
        return Json({'success': True}).http_response(request)

    def request(self, request):
        '''Check for ``HTTP_AUTHORIZATION`` header and if it is available
        and the authentication type if ``bearer`` try to perform
        authentication using JWT_.
        '''
        if not jwt:     # pragma    nocover
            raise ImproperlyConfigured('JWT library not available')
        auth = request.get('HTTP_AUTHORIZATION')
        user = request.cache.user
        if auth and user.is_anonymous():
            auth_type, key = auth.split(None, 1)
            auth_type = auth_type.lower()
            if auth_type == 'bearer':
                try:
                    token = self.decode_token(request, key)
                except Exception:
                    request.app.logger.exception('Could not load user')
                else:
                    request.cache.session = token
                    user = self.get_user(request, **token)
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
