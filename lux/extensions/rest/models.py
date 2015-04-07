from datetime import datetime, timedelta

from lux.extensions.odm import nosql

from .user import (normalise_email, UserMixin, PasswordMixin,
                   MessageMixin, AuthenticationError, READ)
from . import backends


class User(nosql.Model, UserMixin):
    username = nosql.CharField(required=True, minlength=6, maxlength=30)
    password = nosql.PasswordField(maxlength=128)
    name = nosql.CharField()
    surname = nosql.CharField()
    email = nosql.EmailField()
    active = nosql.BooleanField(default=False)
    superuser = nosql.BooleanField(default=False)
    company = nosql.CharField()
    joined = nosql.DateTimeField(default=lambda _: datetime.now())
    # timezone = nosql.CharField(default=default_timezone)
    #
    # oauths = nosql.StructuredProperty(Oauth, repeated=True)
    # messages = nosql.StructuredProperty(Message, repeated=True)

    def is_active(self):
        return self.active

    def is_superuser(self):
        return self.superuser


class Group(nosql.Model):
    name = nosql.CharField()



class Session(nosql.Model, MessageMixin):
    expiry = nosql.DateTimeField()
    user = nosql.ForeignKey(User, required=False)
    access = nosql.IntegerField(default=1)
    agent = nosql.CharField()
    client_address = nosql.CharField()

    def message(self, level, message):
        pass

    def remove_message(self, data):
        pass


class Permission(nosql.Model):
    user = nosql.ForeignKey(User)
    name = nosql.CharField()
    level = nosql.IntegerField()


class Application(nosql.Model):
    user = nosql.ForeignKey(User)
    key = nosql.TextField()
    secret = nosql.TextField()


class AuthMixin(PasswordMixin):

    def authenticate(self, request, user_id=None, username=None, email=None,
                     password=None, **kw):
        manager = request.app.odm('nosql').user
        user = None
        try:
            if user_id:
                user = manager.get(user_id)
            elif username:
                user = manager.get(username=username)
            elif email:
                user = manager.get(email=normalise_email(email))
            else:
                raise AuthenticationError('Invalid credentials')
            if user and self.decript(user.password) == password:
                return user
            else:
                raise odm.ModelNotFound
        except odm.ModelNotFound:
            if username:
                raise AuthenticationError('Invalid username or password')
            elif email:
                raise AuthenticationError('Invalid email or password')
            else:
                raise AuthenticationError('Invalid credentials')

    def set_password(self, user, raw_password):
        user.password = self.password(raw_password)
        user.save()

    def has_permission(self, request, name, level=None):
        user = request.cache.user
        mapper = self.mapper
        level = level or READ
        # Superuser, always true
        if user.is_superuser():
            return True
        else:
            permissions = self._permissions(request)
            p = permissions.get(name)
            if p and p.level >= level:
                return True
            else:
                return False

    def create_user(self, request, username=None, password=None, email=None,
                    name=None, surname=None, active=False, superuser=False,
                    **kwargs):
        manager = request.app.odm('nosql').user
        email = normalise_email(email)
        assert username or email

        if username:
            if manager.filter(username=username).all():
                raise sessions.AuthenticationError(
                    '%s already used' % username)
        if email and manager.filter(email=email).all():
            raise sessions.AuthenticationError('%s already used' % email)

        if not username:
            username = email
            active = False
            registration = False
        else:
            registration = not active

        user = manager(username=username, password=self.password(password),
                       email=email, name=name, surname=surname,
                       active=active, superuser=superuser, **kwargs).save()
        if registration:  # create registration email if user is not active
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

    def _permissions(self, request):
        cache = request.cache.user_roles
        if cache is None:
            mapper = self.mapper
            user = request.cache.user
            if user.is_authenticated():
                query = mapper.permission.filter(user=user)
            else:
                query = mapper.permission.filter(user=None)
            all = query.all()
            cache = dict(((perm.name, perm) for perm in
                          sorted(all, key=lambda p: o.level)))
            request.cache.user_roles = cache
        return cache


class TokenBackend(AuthMixin, backends.TokenBackend):

    def jwt_payload(self, request, user):
        payload = super().jwt_payload(request, user)
        if user.superuser:
            payload['admin'] = True
        return payload


class SessionBackend(AuthMixin, backends.SessionBackend):

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
