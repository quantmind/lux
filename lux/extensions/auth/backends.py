import uuid

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from datetime import datetime

from lux import cached
from lux.utils.crypt import digest
from lux.extensions.rest import (PasswordMixin, backends, normalise_email,
                                 AuthenticationError)
from lux.extensions.rest.policy import has_permission

from .views import Authorization, SignUp


class AuthMixin(PasswordMixin):
    '''Mixin to implement authentication backend based on
    SQLAlchemy models
    '''
    def api_sections(self, app):
        '''At the authorization router to the api
        '''
        yield Authorization()

    def get_user(self, request, user_id=None, token_id=None, username=None,
                 email=None, auth_key=None, **kw):
        '''Securely fetch a user by id, username or email

        Returns user or nothing
        '''
        odm = request.app.odm()

        if token_id and user_id:
            with odm.begin() as session:
                query = session.query(odm.token)
                query = query.filter_by(user_id=user_id, id=token_id)
                query.update({'last_access': datetime.utcnow()},
                             synchronize_session=False)
                if not query.count():
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
        odm = request.app.odm()

        try:
            if not user:
                with odm.begin() as session:
                    query = session.query(odm.user)
                    if user_id:
                        user = query.get(user_id)
                    elif username:
                        user = query.filter_by(username=username).one()
                    elif email:
                        email = normalise_email(email)
                        user = query.filter_by(email=email).one()
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
            permissions = self.get_permissions(request)
            return has_permission(request, permissions, name, level)

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

    def create_token(self, request, user, **kwargs):
        '''Create the token and return a two element tuple
        containing the token and the encoded version
        '''
        odm = request.app.odm()
        ip_address = request.get_client_address()
        user_id = user.id if user.is_authenticated() else None

        with odm.begin(close=False) as session:
            token = odm.token(id=uuid.uuid4(),
                              user_id=user_id,
                              ip_address=ip_address,
                              user_agent=self.user_agent(request, 80),
                              **kwargs)
            session.add(token)
        token.encoded = self.encode_token(request,
                                          token_id=token.id.hex,
                                          user=token.user or user,
                                          expiry=token.expiry)
        session.close()
        return token

    def create_registration(self, request, user, expiry=None, **kw):
        '''Create a registration entry and return the registration id
        '''
        odm = request.app.odm()
        with odm.begin() as session:
            reg = odm.registration(id=digest(user.username),
                                   user_id=user.id,
                                   expiry=expiry,
                                   confirmed=False)
            session.add(reg)

        return reg.id

    def set_password(self, request, user, password):
        '''Set a new password for user
        '''
        with request.app.odm().begin() as session:
            user.password = self.password(password)
            session.add(user)
        return user

    @cached(user=True)
    def get_permissions(self, request):
        odm = request.app.odm()
        user = request.cache.user
        perms = {}
        with odm.begin() as session:
            if user.is_authenticated():
                session.add(user)
                groups = set(user.groups)
            else:
                cfg = request.config
                query = session.query(odm.group)
                groups = set(query.filter_by(name=cfg['ANONYMOUS_GROUP']))
            for group in groups:
                perms.update(((p.name, p.policy) for p in group.permissions))
        return perms


class TokenBackend(AuthMixin, backends.TokenBackend):
    '''Authentication backend based on JSON Web Token
    '''


class SessionBackend(AuthMixin, backends.SessionBackend):
    '''An authentication backend based on sessions stored in the
    cache server and user on the ODM
    '''
    def get_session(self, request, key):
        '''Retrieve a session from its key
        '''
        odm = request.app.odm()
        token = odm.token
        with odm.begin() as session:
            query = session.query(token).options(joinedload(token.user))
            return query.get(key)

    def create_session(self, request, user=None):
        session = super().create_session(request, user=user)
        odm = request.app.odm()
        with odm.begin() as s:
            s.add(session)
            session.user
        return session

    def session_save(self, request, session):
        odm = request.app.odm()
        with odm.begin() as s:
            s.add(session)
        return session


class BrowserBackend(backends.BrowserBackend):
    SignUpRouter = SignUp


class ApiSessionBackend(backends.ApiSessionBackend):
    SignUpRouter = SignUp
