'''A :ref:`lux extension <extensions>` for managing users, sessions
and permissions. The extension is added by inserting
``lux.extensions.sessions`` into the
list of :setting:`EXTENSIONS` of your application.

Messages
==============


'''
import json
from datetime import datetime, timedelta
from importlib import import_module
from functools import wraps

from pulsar import PermissionDenied, Http404
from pulsar.utils.pep import to_bytes, to_string
from pulsar.utils.importer import module_attribute
from pulsar.apps.wsgi import wsgi_request

import lux
from lux import Parameter, Router
from lux.forms import Form
from lux.utils.crypt import get_random_string
from lux.utils.http import same_origin

from .views import *
from .oauth import *
from .backend import *
from .forms import *


REASON_NO_REFERER = "Referer checking failed - no Referer"
REASON_BAD_REFERER = "Referer checking failed - %s does not match %s"
REASON_BAD_TOKEN = "CSRF token missing or incorrect"


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
                  'Number of days the activation code is valid'),
        Parameter('RESET_PASSWORD_URL', '',
                  'If given, add the router to handle password resets'),
        Parameter('CSRF_PARAM', 'authenticity_token',
                  'CSRF parameter name in forms')]

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
        reset = app.config['RESET_PASSWORD_URL']
        if reset:
            router = backend.ForgotPasswordRouter or ForgotPassword
            middleware.append(router(reset))
        return middleware

    def response_middleware(self, app):
        return self._response_middleware

    def on_html_document(self, app, request, doc):
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            param = app.config['CSRF_PARAM']
            csrf_token = app.auth_backend.csrf_token(request)
            if csrf_token and param:
                doc.head.add_meta(name="csrf-param", content=param)
                doc.head.add_meta(name="csrf-token", content=csrf_token)

    def jscontext(self, request, context):
        session = request.cache.session
        context['messages'] = session.get_messages()

    def on_form(self, app, form):
        '''Handle CSRF on form
        '''
        param = app.config['CSRF_PARAM']
        if form.request.method == 'POST' and form.is_bound and param:
            token = form.rawdata.get(param)
            app.auth_backend.validate_csrf_token(form.request, token)

    def _dismiss_message(self, request):
        response = request.response
        if response.content_type in lux.JSON_CONTENT_TYPES:
            session = request.cache.session
            form = Form(request, data=request.body_data())
            data = form.rawdata['message']
            body = {'success': session.remove_message(data)}
            response.content = json.dumps(body)
            return response

    def _check_referer(self, request):
        referer = request.get('HTTP_REFERER')
        if referer is None:
            raise PermissionDenied(REASON_NO_REFERER)
        # Note that request.get_host() includes the port.
        good_referer = 'https://%s/' % request.get_host()
        if not same_origin(referer, good_referer):
            reason = REASON_BAD_REFERER % (referer, good_referer)
            raise PermissionDenied(reason)
