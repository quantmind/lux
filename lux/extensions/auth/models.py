from datetime import datetime, timedelta

import odm

from .sessionmixin import SessionMixin
from .jwtmixin import JWTMixin
from . import backend


class User(odm.Model):
    username = odm.CharField()
    password = odm.CharField()
    name = odm.CharField()
    surname = odm.CharField()
    email = odm.CharField()
    active = odm.BooleanField(default=False)
    superuser = odm.BooleanField(default=False)
    company = odm.CharField()
    joined = odm.DateTimeField(auto_now_add=True)
    #
    #oauths = odm.StructuredProperty(Oauth, repeated=True)
    #messages = odm.StructuredProperty(Message, repeated=True)


class Session(odm.Model):
    user = odm.ForeignKey(User, required=False)
    access = odm.IntegerField(default=1)
    agent = odm.CharField()
    client_address = odm.CharField()


class Permission(odm.Model):
    user = odm.ForeignKey(User)
    name = odm.CharField()
    level = odm.IntegerField()


class AuthBackend(backend.AuthBackend):
    '''Authentication Backend based on :mod:`lux.extensions.odm`
    '''
    @property
    def mapper(self):
        return self.app.mapper

    def has_permission(self, request, level, model):
        user = request.cache.user
        if user.is_superuser():
            return True
        elif level <= self.READ:
            return True
        elif user.is_authenticated():
            cache = request.cache.user_roles
            if cache is None:
                request.cache.user_roles = cache = {}
            p = Permission.get_from_user_and_model(user, model, cache)
            if p and p.level >= level:
                return True
        return False

    def set_password(self, user, raw_password):
        user.password = self.password(raw_password)
        user.save()

    def create_user(self, request, username=None, password=None, email=None,
                    name=None, surname=None, active=False, **kwargs):
        assert username
        email = self.normalise_email(email)
        if self.User.get_by_username(username):
            raise sessions.AuthenticationError('%s already used' % username)
        if email and self.User.get_by_email(email):
            raise sessions.AuthenticationError('%s already used' % email)
        user = self.User(username=username, password=self.password(password),
                         email=email, name=name, surname=surname,
                         active=active)
        user.put()
        if not user.active:  # create registration email if user is not active
            self.get_or_create_registration(request, user)
        return user

    def get_user(self, request, username=None, email=None, auth_key=None,
                 **kw):
        if username:
            assert email is None, 'get_user by username or email'
            assert auth_key is None
            return self.User.get_by_username(username)
        elif email:
            assert auth_key is None
            return self.User.get_by_email(email)
        elif auth_key:
            reg = Registration.get_by_id(auth_key)
            if reg:
                reg.check_valid()
                return reg.user.get()


class SessionBackend(SessionMixin, AuthBackend):

    def get_session(self, id):
        return self.Session.get_by_id(id)

    def session_key(self, session):
        return session.key.id() if session else None

    def create_session(self, request, user=None, expiry=None):
        session = request.cache.session
        if session:
            session.expiry = datetime.now()
            session.put()
        if not expiry:
            expiry = datetime.now() + timedelta(seconds=self.session_expiry)
        client_address = request.get_client_address()
        session = self.mapper.session(
            user=user, expiry=expiry, client_address=client_address,
            agent=request.get('HTTP_USER_AGENT', ''))
        session.save()
        return session

    def get_user_by_email(self, email):
        return self.User.get_by_email(email)

    def create_registration(self, request, user, expiry):
        auth_key = digest(user.username)
        reg = Registration(id=auth_key, user=user.key,
                           expiry=expiry, confirmed=False)
        reg.put()
        return auth_key

    def auth_key_used(self, key):
        reg = Registration.get_by_id(key)
        if reg:
            reg.confirmed = True
            reg.put()

    def confirm_registration(self, request, key=None, **params):
        reg = None
        if key:
            reg = Registration.get_by_id(key)
            if reg:
                user = reg.user.get()
                session = request.cache.session
                if reg.confirmed:
                    session.warning('Registration already confirmed')
                    return user
                # the registration key has expired
                if reg.expiry < datetime.now():
                    session.warning('The confirmation link has expired')
                else:
                    reg.confirmed = True
                    user.active = True
                    user.put()
                    reg.put()
                    session.success('Your email has been confirmed! You can '
                                    'now login')
                    return user
            else:
                raise Http404
        else:
            user = self.get_user(**params)
            self.get_or_create_registration(request, user)


class JWTBackend(JWTMixin, AuthBackend):

    def __init__(self, app):
        super().__init__(app)
        self.User = User
        self.Session = Session
