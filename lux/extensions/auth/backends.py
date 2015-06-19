import uuid

from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime

from lux.extensions.rest import (PasswordMixin, backends, normalise_email,
                                 AuthenticationError, READ)


class AuthMixin(PasswordMixin):
    '''Mixin to implement authentication backend based on
    SQLAlchemy models
    '''

    def get_user(self, request, user_id=None, username=None, email=None, **kw):
        '''Securely fetch a user by id, username or email

        Returns user or nothing
        '''
        odm = request.app.odm()

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
                     password=None, **kw):
        odm = request.app.odm()

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
                    raise AuthenticationError('Invalid credentials')
                if user and self.crypt_verify(user.password, password):
                    return user
                else:
                    raise NoResultFound
            except NoResultFound:
                if username:
                    raise AuthenticationError('Invalid username or password')
                elif email:
                    raise AuthenticationError('Invalid email or password')
                else:
                    raise AuthenticationError('Invalid credentials')

    def has_permission(self, request, name, level):
        user = request.cache.user
        # Superuser, always true
        if user.is_superuser():
            return True
        else:
            if level <= READ:
                return True
            else:
                return False

    def create_user(self, request, username=None, password=None, email=None,
                    first_name=None, last_name=None, active=False,
                    superuser=False, **kwargs):
        '''Create a new user.

        Either ``username`` or ``email`` must be provided.
        '''
        odm = request.app.odm()

        email = normalise_email(email)
        assert username or email

        with odm.begin() as session:
            if not username:
                username = email

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


class TokenBackend(AuthMixin, backends.TokenBackend):
    '''Authentication backend based on JSON Web Token
    '''

    def on_config(self, app):
        super().on_config(app)
        backends.TokenBackend.on_config(self, app)

    def get_user(self, request, user_id=None, token_id=None, **kwargs):
        """
        Securely fetch a user by id, username or email, with
        token UUID validation

        Returns user or nothing
        """

        if token_id:
            odm = request.app.odm()

            with odm.begin() as session:
                query = session.query(odm.token)
                query = query.filter_by(user_id=user_id,
                                        id=token_id)
                query.update({'last_access': datetime.utcnow()},
                             synchronize_session=False)
                if query.first() is not None:
                    return super().get_user(request, user_id=user_id, **kwargs)
        else:
            return super().get_user(request, user_id=user_id, **kwargs)

    def create_token(self, request, user, **kwargs):
        '''Create the token
        '''
        odm = request.app.odm()
        payload = self.jwt_payload(request, user)
        ip_address = request.get_client_address()

        with odm.begin() as session:
            token = odm.token(id=uuid.uuid4(),
                              user_id=user.id,
                              ip_address=ip_address,
                              user_agent=self.user_agent(request, 80),
                              **kwargs)
            session.add(token)

        payload['token_id'] = token.id.hex
        payload['username'] = user.username
        return self.encode_payload(request, payload)


class SessionBackend(AuthMixin,
                     backends.CacheSessionMixin,
                     backends.SessionBackend):
    '''An authentication backend based on sessions stored in the
    cache server and user on the ODM
    '''
