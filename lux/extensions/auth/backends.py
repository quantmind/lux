from pulsar import Http404
from pulsar.utils.importer import module_attribute

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from datetime import datetime

from lux.core import PasswordMixin, AuthenticationError, backend_action
from lux.utils.crypt import create_uuid
from lux.utils.auth import normalise_email
from lux.extensions import rest


def validate_username(request, username):
    module_attribute(request.config['CHECK_USERNAME'])(request, username)


class TokenBackend(PasswordMixin, rest.TokenBackend):
    """Mixin to implement authentication backend based on
    SQLAlchemy models
    """
    @backend_action
    def get_user(self, request, user_id=None, token_id=None, username=None,
                 email=None, auth_key=None, **kw):
        """Securely fetch a user by id, username, email or auth key

        Returns user or nothing
        """
        models = request.app.models
        odm = request.app.odm()
        now = datetime.utcnow()

        if token_id:
            with odm.begin(request=request) as session:
                query = session.query(odm.token)
                query = query.filter_by(id=token_id)
                query.update({'last_access': now},
                             synchronize_session=False)
                try:
                    return query.one().user
                except NoResultFound:
                    return None

        users = models.get('users')
        with users.session(request) as session:
            if auth_key:
                query = models.get('registrations').get_query(session)
                try:
                    reg = query.filter(id=auth_key).one()
                except NoResultFound:
                    return

                if reg.expiry > now:
                    user_id = reg.user_id
                else:
                    return

            query = users.get_query(session)
            try:
                if user_id:
                    user = query.filter(id=user_id).one()
                elif username:
                    user = query.filter(username=username).one()
                elif email:
                    user = query.filter(email=normalise_email(email)).one()
                else:
                    return
            except Http404:
                return

            return user.obj

    @backend_action
    def authenticate(self, request, user=None, password=None, **kw):
        if not user:
            user = self.get_user(request, **kw)
        if user and self.crypt_verify(user.password, password):
            return user
        else:
            raise AuthenticationError('Invalid credentials')

    @backend_action
    def create_user(self, request, username=None, password=None, email=None,
                    first_name=None, last_name=None, active=False,
                    superuser=False, session=None, **kw):
        """Create a new user.

        Either ``username`` or ``email`` must be provided.
        """
        odm = request.app.odm()

        email = normalise_email(email)
        assert username or email
        if username:
            validate_username(request, username)

        with odm.begin(session=session) as session:
            if not username:
                username = email

            if session.query(odm.user).filter_by(username=username).count():
                raise ValueError('Username not available')

            if (email and
                    session.query(odm.user).filter_by(email=email).count()):
                raise ValueError('Email not available')

            user = odm.user(username=username,
                            password=self.password(request, password),
                            email=email,
                            first_name=first_name,
                            last_name=last_name,
                            active=active,
                            superuser=superuser,
                            **kw)
            session.add(user)

        return user

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
            token = query.get(key)
        return token
