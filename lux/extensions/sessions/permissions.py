'''Implement a :class:`djpcms.cms.permissions.PermissionHandler`.'''
import sys
import os
import logging
import time
from hashlib import sha1
from functools import partial
from datetime import datetime, timedelta
from pulsar.utils.importer import import_module
from pulsar.utils.pep import ispy3k, to_string, to_bytes

import lux
from lux import AuthenticationError, coroutine_return

from .crypt import generate_secret_key
from .models import Session

logger = logging.getLogger('lux.sessions')


ANONYMOUS_USER = 'anonymous'
UNUSABLE_PASSWORD = '!'  # This will never be a valid hash


class ModelPermissions(object):

    def __init__(self, user, roles):
        self.user = user
        self.roles = roles

    def has(self, request, action, model):
        level = request.app.config['PERMISSION_LEVELS'].get(action, 0)
        for role in self.roles:
            if role.has_permission(model, level):
                return True
        default = request.app.config['DEFAULT_PERMISSION_LEVEL']
        return level <= request.app.config[
            'PERMISSION_LEVELS'].get(default, 50)


class AuthBackend(lux.AuthBackend):
    '''Permission back-end based sessions and users

.. attribute:: secret_key

    Secret key for encryption SALT

.. attribute:: session_cookie_name

    Session cookie name

.. attribute:: session_expiry

    Session expiry in seconds

    Default: 2 weeks

'''
    def __init__(self, app):
        self.encoding = app.config['ENCODING']
        self.secret_key = app.config['SECRET_KEY'].encode()
        self.session_cookie_name = app.config['SESSION_COOKIE_NAME']
        self.session_expiry = app.config['SESSION_EXPIRY']
        self.salt_size = app.config['AUTH_SALT_SIZE']
        self.csrf = app.config['CSRF_KEY_LENGTH']
        self.check_username = app.config['CHECK_USERNAME']
        algorithm = app.config['CRYPT_ALGORITHM']

        self.crypt_module = import_module(algorithm)

    def middleware(self, app):
        return [self.get_session]

    def response_middleware(self, app):
        return [self.process_response]

    def authenticate(self, request, user, password=None):
        if password is not None:
            password = to_bytes(password, self.encoding)
            encrypted = to_bytes(user.password, self.encoding)
            if self.crypt_module.verify(password, encrypted, self.secret_key):
                return user
            else:
                raise AuthenticationError('Invalid password')

    def login(self, request, user=None):
        """Login a ``user`` if it is already authenticated, otherwise do
        nothing."""
        cache = request.cache
        session = cache.session
        user = user or session.user
        if user:
            if session.user_id != user.id:
                cache.session = yield self._create_session(request, user)
            coroutine_return(user)

    def logout(self, request, user=None):
        session = request.cache.session
        user = user or session.user
        if user.is_authenticated():
            request.cache.session = yield self._create_session(request)
        coroutine_return(True)

    def get_user(self, request, username=None, email=None,
                 session=None, **opt):
        '''Retrieve a user.'''
        if username:
            return request.models.user.get(username=username)
        elif email:
            return request.models.user.get(email=email)
        elif session:
            user = session.user
            if not user:
                self.flush_session(session)
                user = AnonymousUser()
            return user

    def create_user(self, request, username=None, password=None, email=None,
                    is_superuser=False, is_active=True):
        if email:
            try:
                email_name, domain_part = email.strip().split('@', 1)
            except ValueError:
                email = ''
            else:
                email = '@'.join([email_name, domain_part.lower()])
        else:
            email = ''
        if not username:
            username = email
        if self._valid_username(username):
            user = request.models.user(username=username, email=email,
                                       is_superuser=is_superuser,
                                       is_active=is_active)
            return self.set_password(request, user, password)

    def create_superuser(self, request, is_superuser=None, **params):
        return self.create_user(request, is_superuser=True, **params)

    def set_password(self, request, user, raw_password=None):
        if raw_password:
            user['password'] = self._encript(raw_password)
        else:
            user['password'] = UNUSABLE_PASSWORD
        return request.models.user.save(user)

    def has_permission(self, request, action, model):
        if request.cache.session.user.is_superuser:
            return True
        else:
            return request.cache.permissions.has(request, action, model)

    ########################################################################
    # MIDDLEWARE
    def get_session(self, environ, start_response):
        request = lux.wsgi_request(environ)
        request.cache.session = s = yield self._get_session(request)
        request.cache.permissions = yield self._get_permissions(request, s)

    def process_response(self, environ, response):
        """If request.session was modified set a session cookie."""
        if response.can_set_cookies():
            request = lux.wsgi_request(environ)
            session = request.cache.session
            if session is not None:
                if session.must_save:
                    yield session.save()
                if session.modified:
                    response.set_cookie(self.session_cookie_name,
                                        value=session.id,
                                        expires=session.expiry)
        coroutine_return(response)

    ########################################################################
    #    PRIVATE METHODS
    def _valid_username(self, username):
        if username:
            lname = username.lower()
            if lname != ANONYMOUS_USER:
                return self.check_username(username)
        return False

    def _encript(self, password):
        p = self.crypt_module.encrypt(to_bytes(password, self.encoding),
                                      self.secret_key, self.salt_size)
        return to_string(p, self.encoding)

    def _get_session(self, request):
        qs = request.url_data
        session = None
        if 'access_token' in qs:
            session = yield self._session_from_token(request,
                                                     qs['access_token'])
        if session is None and self.session_cookie_name:
            cookie_name = self.session_cookie_name
            cookies = request.response.cookies
            session_key = cookies.get(cookie_name)
            session = None
            if session_key:
                session = yield self._session_from_token(request,
                                                         session_key.value)
            if session is None:
                session = yield self._create_session(request,
                                                     request.cache.user)
        coroutine_return(session)

    def _get_permissions(self, request, session):
        roles = yield session.user.roles.query().all()
        coroutine_return(ModelPermissions(session.user, roles))

    def _session_from_token(self, request, key):
        qs = request.models[Session].query().load_related('user')
        session = yield qs.filter(id=key).all()
        if session:
            session = session[0]
            session.modified = False
            if session.expired:
                yield session.delete()
                session = None
            else:
                # HACK!, need to fix stdnet!
                session.user.session = session.session
                request.cache.user = session.user
        else:
            session = None
        coroutine_return(session)

    def _create_session(self, request, user=None):
        #Create new session and added it to the environment.
        old = request.cache.session
        if isinstance(old, Session):
            old.expiry = datetime.now()
            yield old.save()
        if not user:
            user = yield self._anonymous_user(request)
        expiry = datetime.now() + timedelta(seconds=self.session_expiry)
        pid = os.getpid()
        sa = os.urandom(self.salt_size)
        val = to_bytes("%s%s" % (pid, time.time())) + sa + self.secret_key
        id = sha1(val).hexdigest()
        #session is a reserved attribute in router, use dict access
        session = yield request.models.session.create(id=id, expiry=expiry,
                                                      user=user)
        request.cache.user = session.user
        coroutine_return(session)

    def _anonymous_user(self, request):
        user = yield request.models.user.filter(username=ANONYMOUS_USER).all()
        if user:
            user = user[0]
        else:
            user = request.models.user.new(username=ANONYMOUS_USER,
                                           can_login=False)
        coroutine_return(user)
