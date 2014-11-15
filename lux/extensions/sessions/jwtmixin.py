try:
    import jwt
except ImportError:
    jwt = None

__all__ = ['JWTMixin']


class JWTMixin(object):
    '''Mixin for :class:`.AuthBackend` based on JWT_

    Requires pyjwt_ package.

    .. _pyjwt: https://pypi.python.org/pypi/PyJWT
    .. _JWT: http://self-issued.info/docs/draft-ietf-oauth-json-web-token.html
    '''

    def __init__(self, app):
        self.init_wsgi(app)
        cfg = self.config
        self.secret_key = cfg['SECRET_KEY'].encode()

    def request(self, request):
        '''Check for ``HTTP_AUTHORIZATION`` header and if it is available
        and the authentication type if ``bearer`` try to perform
        authentication using JWT_.
        '''
        auth = request.get('HTTP_AUTHORIZATION')
        user = None
        if auth:
            auth_type, key = auth.split(None, 1)
            auth_type = auth_type.lower()
            if auth_type == 'bearer' and jwt:
                try:
                    data = jwt.decode(key, self.secret_key)
                except jwt.ExpiredSignature:
                    request.app.logger.info('JWT token has expired')
                except Exception:
                    request.app.logger.exception('Could not load user')
                else:
                    user = self.get_user(request, **data)
        request.cache.user = user or self.anonymous()
