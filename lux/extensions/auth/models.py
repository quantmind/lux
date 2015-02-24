from datetime import datetime, timedelta

import odm

from .sessionmixin import SessionMixin
from .jwtmixin import JWTMixin
from .backend import AuthenticationError
from . import backend


class User(odm.Model, backend.UserMixin):
    username = odm.CharField(required=True, minlength=6, maxlength=30)
    password = odm.PasswordField(maxlength=128)
    name = odm.CharField()
    surname = odm.CharField()
    email = odm.EmailField()
    active = odm.BooleanField(default=False)
    superuser = odm.BooleanField(default=False)
    company = odm.CharField()
    joined = odm.DateTimeField(default=lambda _: datetime.now())
    #timezone = odm.CharField(default=default_timezone)
    #
    #oauths = odm.StructuredProperty(Oauth, repeated=True)
    #messages = odm.StructuredProperty(Message, repeated=True)

    def is_active(self):
        return self.active


class Session(odm.Model, backend.MessageMixin):
    expiry = odm.DateTimeField()
    user = odm.ForeignKey(User, required=False)
    access = odm.IntegerField(default=1)
    agent = odm.CharField()
    client_address = odm.CharField()

    def message(self, level, message):
        pass

    def remove_message(self, data):
        pass


class Permission(odm.Model):
    user = odm.ForeignKey(User)
    name = odm.CharField()
    level = odm.IntegerField()


class Application(odm.Model):
    user = odm.ForeignKey(User)
    key = odm.TextField()
    secret = odm.TextField()


class AuthBackend(backend.AuthBackend):
    '''Authentication Backend based on :mod:`lux.extensions.odm`
    '''
    @property
    def mapper(self):
        return self.app.mapper()

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
                    name=None, surname=None, active=False, superuser=False,
                    **kwargs):
        assert username
        manager = self.mapper.user
        email = self.normalise_email(email)
        if manager.filter(username=username).all():
            raise sessions.AuthenticationError('%s already used' % username)
        if email and manager.filter(email=email).all():
            raise sessions.AuthenticationError('%s already used' % email)
        user = manager(username=username, password=self.password(password),
                       email=email, name=name, surname=surname,
                       active=active, superuser=superuser, **kwargs).save()
        if not user.active:  # create registration email if user is not active
            self.get_or_create_registration(request, user)
        return user

    def create_superuser(self, request, **params):
        params['superuser'] = True
        params['active'] = True
        return self.create_user(request, **params)

    def get_user(self, _, username=None, email=None, auth_key=None, **kw):
        try:
            if username:
                assert email is None, 'get_user by username or email'
                assert auth_key is None
                return self.mapper.user.get(username=username)
            elif email:
                assert auth_key is None
                return self.mapper.user.get(email=email)
            elif auth_key:
                reg = Registration.get_by_id(auth_key)
                if reg:
                    reg.check_valid()
                    return reg.user.get()
        except odm.ModelNotFound:
            return None


class SessionBackend(SessionMixin, AuthBackend):

    def get_session(self, id):
        try:
            return self.mapper.session.get(id)
        except odm.ModelNotFound:
            return None

    def session_key(self, session):
        return session.pk if session else None

    def session_save(self, session):
        session.save()

    def session_create(self, request, user=None, expiry=None):
        session = request.cache.session
        if session:
            session.expiry = datetime.now()
            session.save()
        if not expiry:
            expiry = datetime.now() + timedelta(seconds=self.session_expiry)
        client_address = request.get_client_address()
        return self.mapper.session(
            user=user, expiry=expiry, client_address=client_address,
            agent=request.get('HTTP_USER_AGENT', '')).save()

    def authenticate(self, request, username=None, email=None, password=None):
        manager = self.mapper.user
        user = None
        try:
            if username:
                user = manager.get(username=username)
            elif email:
                user = manager.get(email=self.normalise_email(email))
            else:
                raise AuthenticationError('Invalid credentials')
            if user and self.decript(user.password) == password:
                return user
            else:
                raise odm.ModelNotFound
        except odm.ModelNotFound:
            if username:
                raise AuthenticationError('Invalid username or password')
            else:
                raise AuthenticationError('Invalid email or password')

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
