from pulsar.api import Http404, BadRequest

from sqlalchemy.exc import StatementError
from sqlalchemy.orm import joinedload

from lux.core import PasswordMixin, AuthenticationError, backend_action
from lux.utils.crypt import create_uuid
from lux.utils.auth import normalise_email
from lux.utils.data import compact_dict
from lux.ext import rest

from .rest.user import FullUserSchema


class TokenBackend(PasswordMixin, rest.TokenBackend):
    """Mixin to implement authentication backend based on
    SQLAlchemy models
    """
    @backend_action
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
                return reg.user if reg.expiry > now else None
            except Http404:
                return None
        try:
            return models['users'].get_one(session, **compact_dict(
                id=id, username=username, email=normalise_email(email)
            ))
        except Http404:
            return

    @backend_action
    def authenticate(self, session, user=None, password=None, **kw):
        if not user:
            user = self.get_user(session, **kw)
        if user and self.crypt_verify(user.password, password):
            return user
        else:
            raise AuthenticationError('Invalid credentials')

    @backend_action
    def create_user(self, session, **data):
        users = session.models['users']
        data.setdefault('active', True)
        return users.create_one(session, data, FullUserSchema)

    @backend_action
    def create_superuser(self, request, **params):
        params['superuser'] = True
        params['active'] = True
        return self.create_user(request, **params)

    @backend_action
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
