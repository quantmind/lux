'''A :ref:`lux extension <extensions>` for managing user, sessions
and permissions. The extension
is added simply by inserting ``lux.extensions.sessions`` into the
list of ``EXTENSIONS`` of your application.

Parameters
================

.. lux_extension:: lux.extensions.sessions


Permissions
==================

.. automodule:: lux.extensions.sessions.models
'''
from pulsar import PermissionDenied
from pulsar.utils.importer import module_attribute

import lux
from lux import Parameter

from .views import *
from .crypt import get_random_string
from .models import Session


pass_through = lambda u: u


class Extension(lux.Extension):
    '''The sessions extensions provides wsgi middleware for managing sessions
    and users.

    In addition it provides utilities for managing Cross Site Request Forgery
    protection and user permissions levels.
    '''
    _config = [
        Parameter('AUTHENTICATION_BACKENDS',
                  ['lux.extensions.sessions.permissions.AuthBackend'],
                  'A list of python dotted path to a class used to provide '
                  'a backend for authentication. There can be several of '
                  'them.'),
        Parameter('CRYPT_ALGORITHM',
                  'lux.extensions.sessions.crypt.arc4',
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
                  'an action')]

    def middleware(self, app):
        self._response_middleware = []
        middleware = []
        for dotted_path in app.config['AUTHENTICATION_BACKENDS']:
            backend = module_attribute(dotted_path)
            backend = backend(app)
            app.permissions.auth_backends.append(backend)
            middleware.extend(backend.middleware(app))
            self._response_middleware.extend(backend.response_middleware(app))
        return middleware

    def response_middleware(self, app):
        return self._response_middleware

    def on_form(self, app, form):
        '''Handle CSRF if in config.'''
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
            key = session.get('csrf_token')
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
            yield SessionCrud('sessions', models[Session])
            yield UserCrud('users', models.user)
