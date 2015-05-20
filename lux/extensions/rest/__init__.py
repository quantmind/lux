'''
Extension for Restful web services
'''
from datetime import datetime, timedelta
from importlib import import_module
from functools import wraps

from pulsar.utils.pep import to_bytes, to_string
from pulsar.utils.importer import module_attribute
from pulsar.utils.httpurl import is_absolute_uri

import lux
from lux import Parameter, Router
from lux.core.wrappers import wsgi_request
from lux.utils.http import same_origin
from lux.extensions.angular import add_ng_modules

from .user import *
from .models import RestModel
from .views import (RestRoot, RestRouter, RestMixin, change_password,
                    RequirePermission)


def luxrest(url, name):
    '''Dictionary containing the api type and the api url name
    '''
    return {'url': url, 'name': name}


class AuthBackend(lux.Extension):
    '''Interface for extension supporting restful methods
    '''
    def authenticate(self, request, **params):
        '''Authenticate user'''
        pass

    def login(self, request, user):
        '''Login user'''
        pass

    def create_user(self, request, **kwargs):
        '''Create a standard user.'''
        pass

    def create_superuser(self, request, **kwargs):
        '''Create a user with *superuser* permissions.'''
        pass

    def create_token(self, request, user):
        '''Create an athentication token for ``user``'''
        pass

    def get_user(self, request, **kwargs):
        '''Retrieve a user.'''
        pass

    def request(self, request):
        '''Request middleware. Most restful backends implement this method
        '''
        pass

    def has_permission(self, request, target, level):
        '''Check if the given request has permission over ``target``
        element with permission ``level``
        '''
        pass

    def session_expiry(self, request):
        session_expiry = request.config['SESSION_EXPIRY']
        if session_expiry:
            return datetime.now() + timedelta(seconds=session_expiry)

    def user_agent(self, request, max_len=80):
        agent = request.get('HTTP_USER_AGENT')
        return agent[:max_len] if agent else ''


class Extension(AuthBackend):

    _config = [
        Parameter('AUTHENTICATION_BACKENDS', [],
                  'List of python dotted path to classES used to provide '
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
        Parameter('API_URL', '', 'URL FOR THE REST API', True),
        Parameter('API_SEARCH_KEY', 'q',
                  'The query key for full text search'),
        Parameter('API_OFFSET_KEY', 'offset', ''),
        Parameter('API_LIMIT_KEY', 'limit', ''),
        Parameter('API_LIMIT_DEFAULT', 30,
                  'Default number of items returned when no limit '
                  'API_LIMIT_KEY available in the url'),
        Parameter('API_LIMIT_AUTH', 100,
                  ('Maximum number of items returned when user is '
                   'authenticated')),
        Parameter('API_LIMIT_NOAUTH', 30,
                  ('Maximum number of items returned when user is '
                   'not authenticated'))]

    ngModules = ['lux.users']

    def on_config(self, app):
        self.backends = []

        module = import_module(app.meta.module_name)

        for dotted_path in app.config['AUTHENTICATION_BACKENDS']:
            backend = module_attribute(dotted_path)
            if not backend:
                self.logger.error('Could not load backend "%s"', dotted_path)
                continue
            backend = backend()
            backend.setup(app.config, module, app.params)
            self.backends.append(backend)
            app.bind_events(backend, exclude=('on_config',))

        for backend in self.backends:
            if hasattr(backend, 'on_config'):
                backend.on_config(app)

        app.auth_backend = self

    def middleware(self, app):
        middleware = [self]
        for backend in self.backends:
            middleware.extend(backend.middleware(app) or ())

        url = app.config['API_URL']
        # If the api url is not absolute, add the api middleware
        if not is_absolute_uri(url):

            # Add the preflight event
            events = ('on_preflight',)
            app.add_events(events)
            for backend in self.backends:
                app.bind_events(backend, events)

            app.api = api = RestRoot(url)
            middleware.append(api)
            app.config['API_URL'] = str(api.route)
            for extension in app.extensions.values():
                api_sections = getattr(extension, 'api_sections', None)
                if api_sections:
                    for router in api_sections(app):
                        api.add_child(router)

        return middleware

    def response_middleware(self, app):
        middleware = []
        for backend in self.backends:
            middleware.extend(backend.response_middleware(app) or ())
        return middleware

    def api_sections(self, app):
        '''Called by the api extension'''
        for backend in self.backends:
            api_sections = getattr(backend, 'api_sections', None)
            if api_sections:
                for router in api_sections(app):
                    yield router

    def __call__(self, environ, start_response):
        return self.request(wsgi_request(environ))

    # AuthBackend Implementation
    def request(self, request):
        # Inject self as the authentication backend
        cache = request.cache
        cache.user = Anonymous()
        cache.auth_backend = self
        return self._apply_all('request', request)

    def authenticate(self, request, **kwargs):
        return self._apply_all('authenticate', request, **kwargs)

    def login(self, request, user):
        return self._apply_all('login', request, user)

    def create_token(self, request, user):
        return self._apply_all('create_token', request, user)

    def logout(self, request, user=None):
        return self._apply_all('logout', request, user=user)

    def create_user(self, request, **kwargs):
        '''Create a standard user.'''
        return self._apply_all('create_user', request, **kwargs)

    def create_superuser(self, request, **kwargs):
        '''Create a user with *superuser* permissions.'''
        return self._apply_all('create_superuser', request, **kwargs)

    def get_user(self, request, **kwargs):
        return self._apply_all('get_user', request, **kwargs)

    def has_permission(self, request, target, level):
        has = self._apply_all('has_permission', request, target, level)
        return True if has is None else has

    def on_html_document(self, app, request, doc):
        add_ng_modules(doc, self.ngModules)

    def _apply_all(self, method, request, *args, **kwargs):
        for backend in self.backends:
            result = getattr(backend, method)(request, *args, **kwargs)
            if result is not None:
                return result
