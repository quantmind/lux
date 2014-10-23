'''A :ref:`lux extension <extensions>` for managing users, sessions
and permissions. The extension is added by inserting
``lux.extensions.sessions`` into the
list of :setting:`EXTENSIONS` of your application.

There are several :ref:`parameters <parameters-auth>` which can be used
to customise authorisation.

.. automodule:: backend
   :members:
   :member-order: bysource


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
from .backend import *
from .jwtmixin import *
from .forms import *


class Extension(lux.Extension):
    '''The sessions extensions provides wsgi middleware for managing sessions
    and users.

    In addition it provides utilities for managing Cross Site Request Forgery
    protection and user permissions levels.
    '''
    _config = [
        Parameter('AUTHENTICATION_BACKEND',
                  'lux.extensions.sessions.AuthBackend',
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
        Parameter('SESSION_MESSAGES', False, 'Handle session messages'),
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
        Parameter('RESET_PASSWORD_URL', '',
                  'If given, add the router to handle password resets'),
        Parameter('CSRF_EXPIRY', 60*60,
                  'Cross Site Request Forgery token expiry in seconds.'),
        Parameter('CSRF_PARAM', 'authenticity_token',
                  'CSRF parameter name in forms')]

    backend = None

    def middleware(self, app):
        dotted_path = app.config['AUTHENTICATION_BACKEND']
        if dotted_path:
            self.backend = module_attribute(dotted_path)(app)
            return [self.backend]

    def response_middleware(self, app):
        return [self.backend.response_middleware]

    def on_html_document(self, app, request, doc):
        backend = self.backend
        if backend and request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            param = app.config['CSRF_PARAM']
            csrf_token = backend.csrf_token(request)
            if csrf_token and param:
                doc.head.add_meta(name="csrf-param", content=param)
                doc.head.add_meta(name="csrf-token", content=csrf_token)
            session = request.cache.session
            if session:
                doc.jscontext['messages'] = session.get_messages()

    def on_form(self, app, form):
        '''Handle CSRF on form
        '''
        backend = self.backend
        param = app.config['CSRF_PARAM']
        if (backend and form.request.method == 'POST'
                and form.is_bound and param):
            token = form.rawdata.get(param)
            backend.validate_csrf_token(form.request, token)

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
