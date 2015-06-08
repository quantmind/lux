from sqlalchemy.orm.exc import NoResultFound

from lux.extensions.rest import (PasswordMixin, backends, normalise_email,
                                 AuthenticationError, READ)

from .views import Authorization


class AuthMixin(PasswordMixin):
    '''Mixin to implement authentication backend based on
    SQLAlchemy models
    '''

    def get_user(self, request, user_id=None, username=None, email=None,
                 **kw):
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
                if user and self.decript(user.password) == password:
                    return user
                else:
                    raise odm.ModelNotFound
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

    def api_sections(self, app):
        yield Authorization()

    def create_token(self, request, user):
        '''Create the token
        '''
        odm = request.app.odm()
        payload = self.jwt_payload(request, user)
        # FIXME: typo in ip_address
        ip_adderss = request.get_client_address()

        with odm.begin() as session:
            # FIXME: typo in ip_address
            token = odm.token(user_id=user.id,
                              ip_adderss=ip_adderss,
                              user_agent=self.user_agent(request, 80))
            session.add(token)

        payload['token_id'] = token.id
        payload['username'] = user.username
        return self.encode_payload(request, payload)


class SessionBackend(AuthMixin, backends.SessionBackend):
    '''An authentication backend based on sessions stored in the
    cache server and user in SqlAlchemy
    '''
    def get_session(self, key):
        return self.app.cache_server.hmget('session:%s' % key)

    def session_key(self, session):
        '''Session key from session object
        '''
        return session['id']

    def session_save(self, session):
        key = 'session:%s' % session['id']
        self.app.cache_server.hmset(key, session)

    def session_create(self, request, user=None, expiry=None):
        '''Create a new session
        '''
        raise NotImplementedError
