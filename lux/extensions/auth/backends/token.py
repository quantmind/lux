
import time

from pulsar import HttpException, MethodNotAllowed, ImproperlyConfigured

from lux import Parameter
from lux.extensions.api import ApiRouter

try:
    import jwt
except ImportError:
    jwt = None

from .. import AuthBackend
from ..forms import LoginForm


class Http401(HttpException):

    def __init__(self, auth, msg=''):
        headers = [('WWW-Authenticate', auth)]
        super().__init__(msg=msg, status=401, headers=headers)


class TokenBackend(AuthBackend):
    '''Backend based on JWT_

    Requires pyjwt_ package.

    .. _pyjwt: https://pypi.python.org/pypi/PyJWT
    .. _JWT: http://self-issued.info/docs/draft-ietf-oauth-json-web-token.html
    '''
    form = LoginForm

    _config = [
        Parameter('AUTHORIZATION_URL', '/authorizations',
                  'Url for authorizations',
                  True),
    ]

    def on_config(self, app):
        if not jwt:
            raise ImproperlyConfigured('JWT library not available')
        app.require('lux.extensions.api')

    def api_sections(self, app):
        yield Authorization(app.config['AUTHORIZATION_URL'])

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

    def create_token(self, request, user):
        '''Create the token
        '''
        payload = self.jwt_payload(request, user)
        return jwt.encode(payload, cfg['SECRET_KEY'])

    def jwt_payload(self, request, user):
        expiry = self.session_expiry(request)
        payload = {'user_id': user.id}
        if expiry:
            payload['exp'] = int(time.mktime(expiry.timetuple()))
        return payload


class Authorization(ApiRouter):

    def get(self, request):
        '''List all authorizations for the authenticated user
        '''
        user = request.cache.user
        if not user.is_authenticated():
            raise Http401('Token', 'Requires authentication')

    def post(self, request):
        '''Create a new Authorization token
        '''
        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed

        form = self.form(request, data=request.body_data())

        if form.is_valid():
            auth = request.cache.auth_backend
            try:
                user = auth.authenticate(request, **form.cleaned_data)
                auth.login(request, user)
            except AuthenticationError as e:
                form.add_error_message(str(e))
            else:
                token = self.create_token(request, user)
                return Json({'token': token}).http_response(request)

        return Json(form.tojson()).http_response(request)
