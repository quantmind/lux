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
import json
from importlib import import_module
from functools import wraps

from pulsar import PermissionDenied, Http404
from pulsar.utils.pep import to_bytes, to_string
from pulsar.utils.importer import module_attribute

import lux
from lux import Parameter, Router
from lux.utils.crypt import get_random_string

from .views import *
from .oauth import *
from .backend import *
from .forms import *


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
        Parameter('OAUTH_PROVIDERS', {},
                  'Dictionary of OAuth providers'),
        Parameter('ACCOUNT_ACTIVATION_DAYS', 2,
                  'Number of days the activation code is valid')]

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
        middleware.append(Router('_dismiss_message',
                                 post=self._dismiss_message))
        return middleware

    def response_middleware(self, app):
        return self._response_middleware

    def jscontext(self, request, context):
        session = request.cache.session
        context['messages'] = session.get_messages()

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

    def _dismiss_message(self, request):
        response = request.response
        if response.content_type in lux.JSON_CONTENT_TYPES:
            session = request.cache.session
            data = request.body_data()
            body = {'success': session.remove_message(data)}
            response.content = json.dumps(body)
            return response
