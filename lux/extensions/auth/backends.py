import uuid

from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime

from lux.core import (json_message, PasswordMixin, AuthenticationError,
                      backend_action)
from lux.utils.crypt import digest
from lux.utils.auth import normalise_email
from lux.extensions import rest


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
        odm = request.app.odm()
        now = datetime.utcnow()

        if token_id and user_id:
            with odm.begin() as session:
                query = session.query(odm.token)
                query = query.filter_by(user_id=user_id, id=token_id)
                query.update({'last_access': now},
                             synchronize_session=False)
                if not query.count():
                    return

        if auth_key:
            with odm.begin() as session:
                query = session.query(odm.registration)
                reg = query.get(auth_key)
                if reg and reg.expiry > now:
                    if not reg.confirmed:
                        user_id = reg.user_id
                else:
                    return

        with odm.begin() as session:
            query = session.query(odm.user)
            try:
                if user_id:
                    user = query.get(user_id)
                elif username:
                    user = query.filter_by(username=username).one()
                elif email:
                    user = query.filter_by(email=normalise_email(email)).one()
                else:
                    return
            except NoResultFound:
                return

        return user

    def authenticate(self, request, user_id=None, username=None, email=None,
                     user=None, password=None, **kw):
        if not user:
            user = self.get_user(request, user_id=user_id,
                                 username=username, email=email)
        if user and self.crypt_verify(user.password, password):
            return user
        else:
            raise AuthenticationError('Invalid credentials')

    def create_user(self, request, username=None, password=None, email=None,
                    first_name=None, last_name=None, active=False,
                    superuser=False, odm_session=None, **kw):
        """Create a new user.

        Either ``username`` or ``email`` must be provided.
        """
        odm = request.app.odm()

        email = normalise_email(email)
        assert username or email
        if username:
            self.validate_username(request, username)

        with odm.begin(session=odm_session) as session:
            if not username:
                username = email

            if session.query(odm.user).filter_by(username=username).count():
                raise ValueError('Username not available')

            if (email and
                    session.query(odm.user).filter_by(email=email).count()):
                raise ValueError('Email not available')

            user = odm.user(username=username,
                            password=self.password(password),
                            email=email,
                            first_name=first_name,
                            last_name=last_name,
                            active=active,
                            superuser=superuser)
            session.add(user)

        return user

    def create_superuser(self, request, **params):
        params['superuser'] = True
        params['active'] = True
        return self.create_user(request, **params)

    def create_token(self, request, user, **kwargs):
        """Create the token
        """
        odm = request.app.odm()
        ip_address = request.get_client_address()
        user_id = user.id if user.is_authenticated() else None

        with odm.begin() as session:
            token = odm.token(id=uuid.uuid4(),
                              user_id=user_id,
                              ip_address=ip_address,
                              user_agent=self.user_agent(request, 80),
                              **kwargs)
            session.add(token)
        return self.add_encoded(request, token)

    def add_encoded(self, request, token):
        """Inject the ``encoded`` attribute to the token and return the token
        """
        if token:
            odm = request.app.odm()
            with odm.begin() as session:
                session.add(token)
                token.encoded = self.encode_token(request,
                                                  token_id=token.id.hex,
                                                  user=token.user,
                                                  expiry=token.expiry)
        return token

    def create_auth_key(self, request, user, expiry=None, **kw):
        """Create a registration entry and return the registration id
        """
        if not expiry:
            expiry = request.cache.auth_backend.auth_key_expiry(request)
        odm = request.app.odm()
        with odm.begin() as session:
            reg = odm.registration(id=digest(user.username),
                                   user_id=user.id,
                                   expiry=expiry,
                                   confirmed=False)
            session.add(reg)

        return reg.id

    def set_password(self, request, password, user=None, auth_key=None):
        """Set a new password for user
        """
        if not user and auth_key:
            user = self.confirm_auth_key(request, auth_key, True)

        if not user:
            raise AuthenticationError('No user')

        with request.app.odm().begin() as session:
            user.password = self.password(password)
            session.add(user)

        return json_message(request, 'password changed')

    def confirm_auth_key(self, request, key, confirm=False):
        odm = request.app.odm()
        with odm.begin() as session:
            reg = session.query(odm.registration).get(key)
            now = datetime.utcnow()
            if reg and not reg.confirmed and reg.expiry > now:
                if confirm:
                    user = reg.user
                    user.active = True
                    reg.confirmed = True
                    reg.expiry = now
                    session.add(user)
                    session.add(reg)
                    return user
                return True
        return False
