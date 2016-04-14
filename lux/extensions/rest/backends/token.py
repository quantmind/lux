from pulsar import ImproperlyConfigured
from pulsar.utils.pep import to_string

from lux.core import Parameter, Http401

from .mixins import jwt, TokenBackendMixin
from .registration import RegistrationMixin
from .. import AuthBackend, Authorization


class TokenBackend(TokenBackendMixin, RegistrationMixin, AuthBackend):
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

    def api_sections(self, app):
        """This backend add the authorization router to the Rest API
        """
        yield Authorization()

    def login(self, request, user):
        expiry = self.session_expiry(request)
        token = self.create_token(request, user, expiry=expiry)
        token = to_string(token.encoded)
        request.response.status_code = 201
        return {'success': True,
                'token': token}

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
            self.authorize(request, auth)

    def authorize(self, request, auth):
        """Authorize claim

        :param auth: a string containing the authorization information
        """
        auth_type, key = auth.split(None, 1)
        auth_type = auth_type.lower()
        if auth_type == 'bearer':
            try:
                token = self.decode_token(request, key)
            except Http401:
                raise
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

    def on_preflight(self, app, request, methods=None):
        '''Preflight handler
        '''
        headers = request.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
        methods = methods or app.config['CORS_ALLOWED_METHODS']
        response = request.response
        origin = request.get('HTTP_ORIGIN', '*')

        if origin == 'null':
            origin = '*'

        response['Access-Control-Allow-Origin'] = origin
        if headers:
            response['Access-Control-Allow-Headers'] = headers
        response['Access-Control-Allow-Methods'] = methods
