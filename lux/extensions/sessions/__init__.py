'''A :ref:`lux extension <extensions>` for managing users, sessions
and permissions. The extension is added by inserting
``lux.extensions.sessions`` into the
list of :setting:`EXTENSIONS` of your application.


Authentication Backend
=========================

.. autoclass:: AuthBackend
   :members:
   :member-order: bysource
'''
from importlib import import_module
from functools import wraps

from pulsar import PermissionDenied, Http404
from pulsar.utils.importer import module_attribute

import lux
from lux import Parameter
from lux.utils.crypt import get_random_string

from .views import *
from .oauth import *


class AuthenticationError(Exception):
    pass


class AuthBackend(object):
    '''Interface for authentication backends.

    An Authentication backend manage authentication, login, logout and
    several other activities which are required for managing users of
    a web site.
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

    def authenticate(self, request, user, **params):
        '''Authenticate a user'''
        pass

    def login(self, request, user=None):
        '''Login a ``user`` if it is already authenticated, otherwise do
        nothing.'''
        raise NotImplementedError

    def logout(self, request, user=None):
        '''Logout a ``user``
        '''
        session = request.cache.session
        user = user or request.cache.user
        if user and user.is_authenticated():
            request.cache.session = self.create_session(request)
            request.cache.user = Anonymous()

    def get_user(self, request, *args, **kwargs):
        '''Retrieve a user.

        This method can raise an exception if the user could not be found,
        or return ``None``.
        '''
        pass

    def create_session(self, request, user=None, expiry=None):
        '''Create a new session
        '''
        raise NotImplementedError

    def create_user(self, request, *args, **kwargs):
        '''Create a standard user.'''
        pass

    def create_superuser(self, request, *args, **kwargs):
        '''Create a user with *superuser* permissions.'''
        pass

    def middleware(self, app):
        return ()

    def response_middleware(self, app):
        return ()

    def has_permission(self, request, action, model):
        '''Check for permission on a model.'''
        pass


class Extension(lux.Extension):
    '''The sessions extensions provides wsgi middleware for managing sessions
    and users.

    In addition it provides utilities for managing Cross Site Request Forgery
    protection and user permissions levels.
    '''
    _config = [
        Parameter('AUTHENTICATION_BACKEND',
                  'lux.extensions.sessions.permissions.AuthBackend',
                  'Python dotted path to a class used to provide '
                  'a backend for authentication.'),
        Parameter('CRYPT_ALGORITHM',
                  'lux.utils.crypt.arc4',
                  'Python dotted path to module which provides the '
                  '``encrypt`` and ``descript`` method for password and '
                  'sensitive data encryption/decription'),
        Parameter('SECRET_KEY',
                  'secret-key',
                  'A string or bytes used for encripting data. Must be unique '
                  'to the application and long and random enough'),
        Parameter('AUTH_SALT_SIZE', 8,
                  'Salt size for encription algorithm'),
        Parameter('SESSION_COOKIE_NAME', 'LUX',
                  'Name of the cookie which stores session id'),
        Parameter('SESSION_EXPIRY', 7*24*60*60,
                  'Expiry for a session in seconds.'),
        Parameter('CSRF_KEY_LENGTH', 32,
                  'Cross Site Request Forgery KEY LENGTH. If 0, no CSRF '
                  'protection is used.'),
        Parameter('CHECK_USERNAME', lambda u: True,
                  'Check if the username is valid'),
        Parameter('PERMISSION_LEVELS', {'read': 10,
                                        'create': 20,
                                        'update': 30,
                                        'delete': 40},
                  'When a model'),
        Parameter('DEFAULT_PERMISSION_LEVEL', 'read',
                  'When no roles has tested positive for permissions, this '
                  'parameter is used to check if a model has permission for '
                  'an action'),
        Parameter('LOGIN_PROVIDERS', {},
                  'Dictionary of OAuth providers')]

    def middleware(self, app):
        self._response_middleware = []
        middleware = []
        dotted_path = app.config['AUTHENTICATION_BACKEND']
        if dotted_path:
            backend = module_attribute(dotted_path)(app)
            app.auth_backend = backend
            middleware.extend(backend.middleware(app))
            self._response_middleware.extend(backend.response_middleware(app))
        else:
            raise RuntimeError('AUTHENTICATION_BACKEND not available')
        return middleware

    def response_middleware(self, app):
        return self._response_middleware

    def on_form(self, app, form):
        '''Handle CSRF if in config.'''
        return
        request = form.request
        if form.is_bound:
            token = self.get_or_create_csrf_token(request)
            form_token = form.rawdata.get('__csrf_token__')
            if token != form_token:
                raise PermissionDenied('CSRF token mismatch')
        else:
            token = self.get_or_create_csrf_token(request)
            if token:
                form.add_input('__csrf_token__', value=token)

    def get_or_create_csrf_token(self, request):
        '''Create or retrieve a CSRF token for this section.
        '''
        session = request.cache.session
        if session:
            key = session.csrf_token
            if not key:
                length = request.app.config['CSRF_KEY_LENGTH']
                if length > 0:
                    key = get_random_string(length)
                    session['csrf_token'] = key
            return key

    def api_sections(self, app):
        '''API routes'''
        yield 'User and sessions', self.api_routes(app)

    def api_routes(self, app):
        models = app.models
        if not models:
            self.logger.warning('Session extensions requires model extension')
        else:
            yield SessionCrud('sessions', models.session)
            yield UserCrud('users', models.user)


class UserMixin(object):

    def is_authenticated(self):
        return True

    def is_active(self):
        return False

    def is_anonymous(self):
        return False

    def get_id(self):
        raise NotImplementedError


class Anonymous(UserMixin):

    def is_authenticated(self):
        return False

    def is_anonymous(self):
        return True

    def get_id(self):
        return 0
