'''Google appengine utilities
'''
import os
import time
from datetime import datetime, timedelta

from pulsar import PermissionDenied, Http404
from pulsar.apps.wsgi import wsgi_request

import lux
from lux.extensions import sessions
from lux.utils.crypt import digest
from lux.extensions.sessions import (SessionMixin, JWTMixin,
                                     AuthenticationError)

from .models import ndb, User, Session, Registration, Permission, role_name
from .api import *


isdev = lambda: os.environ.get('SERVER_SOFTWARE', '').startswith('Development')



class AuthBackend(sessions.AuthBackend):
    '''A :class:`.AuthBackend` for the google app engine
    '''
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
        user.put()

    def auth_key_used(self, key):
        reg = Registration.get_by_id(key)
        if reg:
            reg.confirmed = True
            reg.put()

    def authenticate(self, request, username=None, email=None, password=None):
        user = None
        if username:
            user = self.User.get_by_username(username)
        elif email:
            user = self.User.get_by_email(self.normalise_email(email))
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
        if self.User.get_by_username(username):
            raise sessions.AuthenticationError('%s already used' % username)
        if email and self.User.get_by_email(email):
            raise sessions.AuthenticationError('%s already used' % email)
        user = self.User(username=username, password=self.password(password),
                         email=email, name=name, surname=surname,
                         active=active)
        user.put()
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

    def __init__(self, app, user_class=None, session_class=None):
        super(SessionBackend, self).__init__(app)
        self.User = user_class or User
        self.Session = session_class or Session

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
        session = self.Session(id=self.create_session_id(),
                               user=user.key if user else None,
                               expiry=expiry,
                               client_address=request.get_client_address(),
                               agent=request.get('HTTP_USER_AGENT', ''))
        session.put()
        return session

    def get_user_by_email(self, email):
        return self.User.get_by_email(email)

    def create_registration(self, request, user, expiry):
        auth_key = digest(user.username)
        reg = Registration(id=auth_key, user=user.key,
                           expiry=expiry, confirmed=False)
        reg.put()
        return auth_key

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

    def __init__(self, app, user_class=None):
        super(JWTBackend, self).__init__(app)
        self.User = user_class or User
