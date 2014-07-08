'''Google appengine utilities
'''
import os
import time
from datetime import datetime, timedelta

from pulsar import PermissionDenied
from pulsar.apps.wsgi import wsgi_request

import lux
from lux.extensions import sessions
from lux.utils.crypt import digest, get_random_string
from lux.extensions.sessions import AuthenticationError, REASON_BAD_TOKEN

try:
    import jwt
except ImportError:
    jwt = None

from .models import ndb, Session, Registration, UserRole
from .oauth import User
from .api import *


isdev = lambda: os.environ.get('SERVER_SOFTWARE', '').startswith('Development')


def role_name(model):
    if isinstance(model, ndb.Model):
        model = model.__class__
    return model.__name__.lower()


class GaeBackend(sessions.AuthBackend):
    model = User

    def has_permission(self, request, level, model):
        user = request.cache.user
        if user.is_superuser:
            return True
        elif level <= self.READ:
            return True
        elif user.is_authenticated():
            roles = request.cache.user_roles
            if roles is None:
                request.cache.user_roles = roles = UserRole.get_by_user(user)
            name = role_name(model)
            for role in roles:
                if role.name == name and role.level >= level:
                    return True
        return False

    def decode_jwt(self, token):
        data = jwt.decode(token, self.secret_key)
        expiry = data.get('expiry')
        if expiry and time.time() > expiry:
            raise PermissionDenied('Session expired, try reloading the page')
        return data


class AuthBackend(GaeBackend):
    '''Authentication backend for Google app-engine
    '''
    model = User
    csrf_expiry = 12*60*60

    def middleware(self, app):
        return [self._load]

    def response_middleware(self, app):
        return [self._save]

    def csrf_token(self, request):
        session = request.cache.session
        if session:
            assert jwt, 'Requires jwt package'
            return jwt.encode({'session': session.key.id(),
                               'expiry': time.time() + self.csrf_expiry},
                              self.secret_key)

    def validate_csrf_token(self, request, token):
        if not token:
            raise PermissionDenied(REASON_BAD_TOKEN)
        token = self.decode_jwt(token)
        if token['session'] != request.cache.session.key.id():
            raise PermissionDenied(REASON_BAD_TOKEN)

    def create_registration(self, request, user, expiry):
        auth_key = digest(user.username)
        reg = Registration(id=auth_key, user=user.key,
                           expiry=expiry, confirmed=False)
        reg.put()
        return auth_key

    def set_password(self, user, raw_password):
        user.password = self.password(raw_password)
        user.put()

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
                    return user
        else:
            user = self.get_user(**params)
            self._get_or_create_registration(request, user)

    def authenticate(self, request, username=None, email=None, password=None):
        user = None
        if username:
            user = User.get_by_username(username)
        elif email:
            user = User.get_by_email(self.normalise_email(email))
        else:
            raise AuthenticationError('Invalid credentials')
        if user and self.decript(user.password) == password:
            return user
        else:
            if username:
                raise AuthenticationError('Invalid username or password')
            else:
                raise AuthenticationError('Invalid email or password')

    def create_user(self, request, username=None, password=None, email=None,
                    name=None, surname=None, active=False, **kwargs):
        assert username
        email = self.normalise_email(email)
        if self.model.get_by_username(username):
            raise sessions.AuthenticationError('%s already used' % username)
        if email and self.model.get_by_email(email):
            raise sessions.AuthenticationError('%s already used' % email)
        user = User(username=username, password=self.password(password),
                    email=email, name=name, surname=surname, active=active)
        user.put()
        self._get_or_create_registration(request, user)
        return user

    def create_session(self, request, user=None, expiry=None):
        session = request.cache.session
        if session:
            session.expiry = datetime.now()
            session.put()
        if not expiry:
            expiry = datetime.now() + timedelta(seconds=self.session_expiry)
        session = Session(id=self._create_session_id(user),
                          user=user.key if user else None,
                          expiry=expiry,
                          client_address=request.get_client_address(),
                          agent=request.get('HTTP_USER_AGENT', ''))
        session.put()
        return session

    def get_user(self, request, username=None, email=None, auth_key=None):
        if username:
            assert email is None, 'get_user by username or email'
            assert auth_key is None
            return User.get_by_username(username)
        elif email:
            assert auth_key is None
            return User.get_by_email(email)
        elif auth_key:
            reg = Registration.get_by_id(auth_key)
            if reg:
                reg.check_valid()
                return reg.user.get()

    def _load(self, environ, start_response):
        request = wsgi_request(environ)
        key = request.app.config['SESSION_COOKIE_NAME']
        session_key = request.cookies.get(key)
        session = None
        if session_key:
            session = Session.get_by_id(session_key.value)
        if not session:
            session = self.create_session(request)
        request.cache.session = session
        if session.user:
            request.cache.user = session.user.get()
        else:
            request.cache.user = sessions.Anonymous()

    def _save(self, environ, response):
        request = wsgi_request(environ)
        session = request.cache.session
        if session:
            if response.can_set_cookies():
                key = request.app.config['SESSION_COOKIE_NAME']
                session_key = request.cookies.get(key)
                id = str(session.key.id())
                if not session_key or session_key.value != id:
                    response.set_cookie(key, value=str(id), httponly=True,
                                        expires=session.expiry)

            session.put()
        return response

    def _create_session_id(self, user):
        while True:
            session_key = get_random_string(32)
            if not Session.get_by_id(session_key):
                break
        return session_key


class JwtBackend(GaeBackend):
    '''Authentication backend based on JWT
    '''

    def middleware(self, app):
        return [self._load]

    def get_user(self, request, username=None, email=None, auth_key=None):
        if username:
            assert email is None, 'get_user by username or email'
            assert auth_key is None
            return self.model.get_by_username(username)
        elif email:
            assert auth_key is None
            return self.model.get_by_email(email)
        elif auth_key:
            assert jwt, 'jwt library required'
            data = jwt.decode(auth_key, self.secret_key)
            return self.model.get_by_username(data['username'])

    def _load(self, environ, start_response):
        request = wsgi_request(environ)
        auth = request.get('HTTP_AUTHORIZATION')
        user = None
        if auth:
            auth_type, key = auth.split(None, 1)
            auth_type = auth_type.lower()
            if auth_type == 'bearer':
                try:
                    user = self.get_user(request, auth_key=key)
                except Exception:
                    request.app.logger.exception('Could not load user')
        request.cache.user = user or sessions.Anonymous()
