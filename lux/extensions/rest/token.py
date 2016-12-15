import time
from datetime import datetime, timedelta
from pulsar import Http401, BadRequest, PermissionDenied
from pulsar.utils.pep import to_string

import lux.utils.token as jwt
from lux.core import backend_action, UserMixin
from .permissions import PemissionsMixin


# Cross-Origin Resource Sharing header
CORS = 'Access-Control-Allow-Origin'


class ServiceUser(UserMixin):

    def __init__(self, request):
        self._authenticated = bool(request.cache.token)

    def is_superuser(self):
        return self._authenticated

    def is_authenticated(self):
        return self._authenticated

    def is_anonymous(self):
        return True

    def is_active(self):
        return False


class TokenBackend(PemissionsMixin):
    """Token Backend
    """
    service_user = ServiceUser

    @backend_action
    def login(self, request, user):
        """Handle a request for a token to be used on a web browser
        """
        seconds = request.config['MAX_TOKEN_SESSION_EXPIRY']
        expiry = datetime.now() + timedelta(seconds=seconds)
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
        auth = request.get('HTTP_AUTHORIZATION')
        user = request.cache.user
        if auth and user.is_anonymous():
            self.authorize(request, auth)

    @backend_action
    def authorize(self, request, auth):
        """Authorize claim

        :param auth: a string containing the authorization information
        """
        user = None
        try:
            try:
                auth_type, key = auth.split(None, 1)
            except ValueError:
                raise BadRequest('Invalid Authorization header') from None
            auth_type = auth_type.lower()
            if auth_type == 'bearer':
                token = self.get_token(request, key)
                if not token:
                    raise BadRequest
                request.cache.token = token
                user = token.user
            elif auth_type == 'jwt':
                token = self.decode_token(request, key)
                request.cache.token = token
                user = self.service_user(request)
        except (Http401, BadRequest, PermissionDenied):
            raise
        except Exception:
            request.app.logger.exception('Could not authorize')
            raise BadRequest from None
        else:
            if user:
                request.cache.user = user

    def response(self, response):
        if CORS not in response.headers:
            origin = response.environ.get('HTTP_ORIGIN', '*')
            response[CORS] = origin
        return response

    def response_middleware(self, app):
        return [self.response]

    def encode_token(self, request, user=None, expiry=None, **token):
        """Encode a JWT
        """
        if expiry:
            token['exp'] = int(time.mktime(expiry.timetuple()))

        request.app.fire('on_token', request, token, user)
        return jwt.encode_json(token, request.config['SECRET_KEY'])

    def decode_jwt(self, request, token, key=None,
                   algorithm=None, **options):
        algorithm = algorithm or request.config['JWT_ALGORITHM']
        try:
            return jwt.decode(token, key=key, algorithm=algorithm,
                              options=options)
        except jwt.ExpiredSignature:
            request.app.logger.warning('JWT token has expired')
            raise Http401('Token')
        except jwt.DecodeError as exc:
            request.app.logger.warning(str(exc))
            raise BadRequest

    def decode_token(self, request, token):
        payload = self.decode_jwt(request, token, verify_signature=False)
        secret = self.secret_from_jwt_payload(request, payload)
        return self.decode_jwt(request, token, secret)

    def secret_from_jwt_payload(self, request, payload):
        return request.config['SECRET_KEY']

    def create_token(self, request, user, **kwargs):  # pragma    nocover
        """Create a new token and store it
        """
        raise NotImplementedError

    def get_token(self, request, token):
        """Load a token
        """
        raise NotImplementedError
