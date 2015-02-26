'''A :ref:`lux extension <extensions>` for managing users, sessions
and permissions. The extension is added by inserting
``lux.extensions.auth`` into the
list of :setting:`EXTENSIONS` of your application.

There are several :ref:`parameters <parameters-auth>` which can be used
to customise authorisation.

Authentication Backend
========================

.. automodule:: lux.extensions.auth.backend
   :members:
   :member-order: bysource

.. automodule:: lux.extensions.auth.sessionmixin
   :members:
   :member-order: bysource

.. automodule:: lux.extensions.auth.jwtmixin
   :members:
   :member-order: bysource
'''
from datetime import datetime, timedelta
from importlib import import_module
from functools import wraps

from pulsar import PermissionDenied, Http404
from pulsar.utils.pep import to_bytes, to_string
from pulsar.utils.importer import module_attribute

import lux
from lux import Parameter, Router
from lux.utils.http import same_origin
from lux.extensions.angular import add_ng_modules

from .views import *
from .backend import *
from .jwtmixin import *
from .sessionmixin import *
from .forms import *


class Extension(lux.Extension):
    '''The sessions extensions provides wsgi middleware for managing sessions
    and users.

    In addition it provides utilities for managing Cross Site Request Forgery
    protection and user permissions levels.
    '''
    _config = [
        Parameter('AUTHENTICATION_BACKEND', None,
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
        Parameter('SESSION_MESSAGES', True, 'Handle session messages'),
        Parameter('SESSION_EXPIRY', 7*24*60*60,
                  'Expiry for a session in seconds.'),
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
        Parameter('ACCOUNT_ACTIVATION_DAYS', 2,
                  'Number of days the activation code is valid'),
        Parameter('LOGIN_URL', '/login', 'Url to login'),
        Parameter('LOGOUT_URL', '/logout', 'Url to logout'),
        Parameter('REGISTER_URL', '/signup', 'Url to register with site'),
        Parameter('RESET_PASSWORD_URL', '/reset-password',
                  'If given, add the router to handle password resets'),
        Parameter('CSRF_EXPIRY', 60*60,
                  'Cross Site Request Forgery token expiry in seconds.'),
        Parameter('CSRF_PARAM', 'authenticity_token',
                  'CSRF parameter name in forms'),
        Parameter('DEFAULT_TIMEZONE', 'GMT',
                  'Default timezone'),
        Parameter('ADD_AUTH_ROUTES', True,
                  'Add available authentication Routes')]

    backend = None
    ngModules = ['lux.users']

    def middleware(self, app):
        cfg = app.config
        dotted_path = cfg['AUTHENTICATION_BACKEND']
        middleware = []
        if dotted_path:
            self.backend = module_attribute(dotted_path)(app)
            middleware.extend(self.backend.wsgi())
        if cfg['ADD_AUTH_ROUTES']:
            if cfg['LOGIN_URL']:
                middleware.append(Login(cfg['LOGIN_URL']))
                middleware.append(Logout(cfg['LOGOUT_URL']))
            if cfg['REGISTER_URL']:
                middleware.append(SignUp(cfg['REGISTER_URL']))
            if cfg['RESET_PASSWORD_URL']:
                middleware.append(ForgotPassword(cfg['RESET_PASSWORD_URL']))
        return middleware

    def response_middleware(self, app):
        if self.backend:
            return [self.backend.response_middleware]

    def on_html_document(self, app, request, doc):
        add_ng_modules(doc, self.ngModules)
        backend = request.cache.auth_backend
        if backend and request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            cfg = app.config
            param = cfg['CSRF_PARAM']
            csrf_token = backend.csrf_token(request)
            if param:
                if not csrf_token:
                    raise PermissionDenied(REASON_BAD_TOKEN)
                doc.head.add_meta(name="csrf-param", content=param)
                doc.head.add_meta(name="csrf-token", content=csrf_token)
            session = request.cache.session
            messages = []
            if session:
                messages.extend(session.get_messages())
            user = request.cache.user
            if user:
                messages.extend(user.get_messages())
                doc.jscontext['user'] = user.todict()
            if messages:
                doc.jscontext['messages'] = messages
            # authentication urls
            doc.jscontext['loginUrl'] = cfg['LOGIN_URL']
            doc.jscontext['registerUrl'] = cfg['REGISTER_URL']
            doc.jscontext['resetPasswordUrl'] = cfg['RESET_PASSWORD_URL']

    def on_form(self, app, form):
        '''Handle CSRF on form
        '''
        request = form.request
        backend = request.cache.auth_backend if request else None
        param = app.config['CSRF_PARAM']
        if (backend and form.request.method == 'POST' and
                form.is_bound and param):
            token = form.rawdata.get(param)
            backend.validate_csrf_token(form.request, token)

    def _check_referer(self, request):
        referer = request.get('HTTP_REFERER')
        if referer is None:
            raise PermissionDenied(REASON_NO_REFERER)
        # Note that request.get_host() includes the port.
        good_referer = 'https://%s/' % request.get_host()
        if not same_origin(referer, good_referer):
            reason = REASON_BAD_REFERER % (referer, good_referer)
            raise PermissionDenied(reason)
