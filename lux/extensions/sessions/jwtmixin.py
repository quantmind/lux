'''
.. _JWT: http://self-issued.info/docs/draft-ietf-oauth-json-web-token.html
'''
try:
    import jwt
except ImportError:
    jwt = None

__all__ = ['JWTMixin']


class JWTMixin(object):
    '''Mixin for a :class:`.AuthBackend` based on JWT_
    '''

    def __init__(self, app):
        self.app = app
        cfg = self.config
        self.secret_key = cfg['SECRET_KEY'].encode()

    def request(self, request):
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

    def response(self, request, response):
        pass
