from datetime import datetime

from pulsar.api import BadRequest, Http401, PermissionDenied, Http404

from sqlalchemy.exc import StatementError
from sqlalchemy.orm import joinedload

from lux.core import AuthenticationError, AuthBackend as AuthBackendBase
from lux.utils.crypt import create_uuid
from lux.utils.auth import normalise_email
from lux.utils.data import compact_dict

from .rest.user import CreateUserSchema


class AuthBackend(AuthBackendBase):
    """Mixin to implement authentication backend based on
    SQLAlchemy models
    """
    def on_request(self, request):
        auth = request.get('HTTP_AUTHORIZATION')
        cache = request.cache
        cache.user = self.anonymous()
        if not auth:
            return
        app = request.app
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
                payload = self.decode_jwt(request, key)
                payload['token'] = key
                user = app.auth.service_user(payload)
        except (Http401, BadRequest, PermissionDenied):
            raise
        except Exception:
            request.app.logger.exception('Could not authorize')
            raise BadRequest from None
        else:
            if user:
                request.cache.user = user

    def get_user(self, session, id=None, token_id=None, username=None,
                 email=None, auth_key=None, **kw):
        """Securely fetch a user by id, username, email or auth key

        Returns user or nothing
        """
        models = session.models
        if token_id:
            try:
                return models['tokens'].get_one(session, id=token_id).user
            except Http404:
                return None
        if auth_key:
            try:
                reg = models['registrations'].get_one(session, id=auth_key)
                return reg.user if reg.expiry > datetime.now() else None
            except Http404:
                return None
        try:
            return models['users'].get_one(session, **compact_dict(
                id=id, username=username, email=normalise_email(email)
            ))
        except Http404:
            return

    def authenticate(self, session, user=None, password=None, **kw):
        if not user:
            user = self.get_user(session, **kw)
        if user and self.crypt_verify(user.password, password):
            return user
        else:
            raise AuthenticationError('Invalid credentials')

    def create_user(self, session, **data):
        users = session.models['users']
        data.setdefault('active', True)
        return users.create_one(session, data, CreateUserSchema)

    def create_superuser(self, session, **params):
        params['superuser'] = True
        params['active'] = True
        return self.create_user(session, **params)

    def create_token(self, request, user, **kwargs):
        """Create the token
        """
        odm = request.app.odm()
        with odm.begin() as session:
            kwargs['id'] = create_uuid()
            token = odm.token(user=user, **kwargs)
            session.add(token)
        return token

    def get_token(self, request, key):
        odm = request.app.odm()
        token = odm.token
        with odm.begin() as session:
            query = session.query(token).options(joinedload(token.user))
            try:
                token = query.get(key)
            except StatementError:
                raise BadRequest from None
        return token
