'''
Extension for Restful web services
'''
from importlib import import_module

from pulsar import ImproperlyConfigured
from pulsar.utils.importer import module_attribute
from pulsar.utils.httpurl import is_absolute_uri

from lux import Parameter
from lux.core.wrappers import wsgi_request

from .user import *     # noqa
from .auth import AuthBackend
from .models import RestModel, RestColumn
from .pagination import Pagination, GithubPagination
from .client import ApiClient
from .views import RestRoot, RestRouter, RestMixin, RequirePermission

__all__ = ['RestRouter', 'RestMixin', 'RestModel', 'RestColumn',
           'Pagination', 'GithubPagination', 'AuthBackend',
           'RequirePermission']


def luxrest(url, name, **rest):
    '''Dictionary containing the api type and the api url name
    '''
    rest['url'] = url
    rest['name'] = name
    return rest


class Extension(AuthBackend):

    _config = [
        Parameter('AUTHENTICATION_BACKENDS', [],
                  'List of python dotted paths to classes which provide '
                  'a backend for authentication.'),
        Parameter('CRYPT_ALGORITHM',
                  'lux.utils.crypt.arc4',
                  'Python dotted path to module which provides the '
                  '``encrypt`` and, optionally, ``decrypt`` method for '
                  'password and sensitive data encryption/decryption'),
        Parameter('SECRET_KEY',
                  'secret-key',
                  'A string or bytes used for encrypting data. Must be unique '
                  'to the application and long and random enough'),
        Parameter('AUTH_SALT_SIZE', 8,
                  'Salt size for encryption algorithm'),
        Parameter('SESSION_MESSAGES', True, 'Handle messages'),
        Parameter('SESSION_EXPIRY', 7*24*60*60,
                  'Expiry for a session/token in seconds.'),
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
        Parameter('API_LIMIT_DEFAULT', 25,
                  'Default number of items returned when no limit '
                  'API_LIMIT_KEY available in the url'),
        Parameter('API_LIMIT_AUTH', 100,
                  ('Maximum number of items returned when user is '
                   'authenticated')),
        Parameter('API_LIMIT_NOAUTH', 30,
                  ('Maximum number of items returned when user is '
                   'not authenticated')),
        Parameter('API_AUTHENTICATION_TOKEN', None,
                  'Authentication token for the api. This is used by '
                  'a lux application accessing a lux api'),
        Parameter('PAGINATION', 'lux.extensions.rest.Pagination',
                  'Pagination class')]

    def on_config(self, app):
        self.backends = []

        url = app.config['API_URL']
        if not is_absolute_uri(url):
            app.config['API_URL'] = str(RestRoot(url))

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
            dotted_path = app.config['PAGINATION']
            pagination = module_attribute(dotted_path)
            if not pagination:
                raise ImproperlyConfigured('Could not loaf paginator "%s"',
                                           dotted_path)
            app.pagination = pagination()

            # Add the preflight event
            events = ('on_preflight',)
            app.add_events(events)
            for backend in self.backends:
                app.bind_events(backend, events)

            api = RestRoot(url)
            middleware.append(api)
            for extension in app.extensions.values():
                api_sections = getattr(extension, 'api_sections', None)
                if api_sections:
                    for router in api_sections(app):
                        api.add_child(router)
        app.api = ApiClient(app)
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
        cache.user = self.anonymous()
        cache.auth_backend = self
        return self._apply_all('request', request)

    # HTTP Responses
    def login_response(self, request, user):
        return self._apply_all('login_response', request, user)

    def logout_response(self, request, user):
        return self._apply_all('logout_response', request, user)

    def signup_response(self, request, user):
        return self._apply_all('signup_response', request, user)

    def password_changed_response(self, request, user):
        return self._apply_all('password_changed_response', request, user)

    # Backend methods
    def authenticate(self, request, **kwargs):
        return self._apply_all('authenticate', request, **kwargs)

    def create_user(self, request, **kwargs):
        '''Create a standard user.'''
        return self._apply_all('create_user', request, **kwargs)

    def create_superuser(self, request, **kwargs):
        '''Create a user with *superuser* permissions.'''
        return self._apply_all('create_superuser', request, **kwargs)

    def get_user(self, request, **kwargs):
        return self._apply_all('get_user', request, **kwargs)

    def create_token(self, request, user, **kwargs):
        return self._apply_all('create_token', request, user, **kwargs)

    def has_permission(self, request, target, level):
        has = self._apply_all('has_permission', request, target, level)
        return True if has is None else has

    def _apply_all(self, method, request, *args, **kwargs):
        for backend in self.backends:
            result = getattr(backend, method)(request, *args, **kwargs)
            if result is not None:
                return result
