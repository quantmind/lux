"""
Extension for Restful web services.

This extension should be added before any other extensions
which requires authentication and restful services.
When using default lux extensions, the usual position of this extension is
just after the :mod:`lux.extensions.base`::

    EXTENSIONS = ['lux.extensions.base',
                  'lux.extensions.rest',
                  ...
                  ]

"""
from urllib.parse import urljoin, urlparse
from collections import OrderedDict

from pulsar import ImproperlyConfigured
from pulsar.utils.importer import module_attribute
from pulsar.utils.httpurl import is_absolute_uri, remove_double_slash
from pulsar.apps.wsgi import wsgi_request

from lux.core import Parameter

from .auth import AuthBackend, MultiAuthBackend, backend_action
from .models import RestModel, RestField, is_rel_field
from .client import ApiClient
from .views.actions import (AuthenticationError, check_username, login,
                            logout, user_permissions)
from .views.rest import RestRoot, RestRouter, MetadataMixin, CRUD, Rest404
from .views.auth import Authorization
from .pagination import Pagination, GithubPagination
from .forms import RelationshipField, UniqueField
from .query import Query, RestSession
from .user import (MessageMixin, UserMixin, SessionMixin, PasswordMixin,
                   User, Session, session_backend)


__all__ = ['RestModel',
           'RestField',
           'is_rel_field',
           #
           'Authorization',
           #
           'AuthBackend',
           'backend_action',
           #
           'RestRouter',
           'MetadataMixin',
           'CRUD',
           #
           'Query',
           'RestSession',
           #
           'Pagination',
           'GithubPagination',
           'AuthenticationError',
           'MessageMixin',
           'UserMixin',
           'SessionMixin',
           'PasswordMixin',
           'User',
           'Session',
           'session_backend',
           #
           # Form fields related to rest models
           'RelationshipField',
           'UniqueField',
           #
           'api_url',
           'api_path',
           #
           'login',
           'logout',
           'user_permissions',
           'check_username']


def website_url(request, location=None):
    """A website url
    """
    url = request.config.get('WEB_SITE_URL')
    url = url or request.absolute_uri('/')
    if location:
        url = urljoin(url, location)
    return url


def api_url(request, location=None):
    url = request.config.get('API_URL')
    url = url or request.absolute_uri('/')
    if location:
        url = urljoin(url, location)
    return url


def api_path(request, model, *args):
    model = request.app.models.get(model)
    if model:
        path = urlparse(model.api_url(request)).path
        return '%s/%s' % (path, '/'.join(args)) if args else path


class Extension(MultiAuthBackend):

    _config = [
        Parameter('AUTHENTICATION_BACKENDS', [],
                  'List of python dotted paths to classes which provide '
                  'a backend for authentication.'),
        Parameter('CRYPT_ALGORITHM',
                  'lux.utils.crypt.pbkdf2',
                  # dict(module='lux.utils.crypt.arc4', salt_size=8),
                  'Python dotted path to module which provides the '
                  '``encrypt`` and, optionally, ``decrypt`` method for '
                  'password and sensitive data encryption/decryption'),
        Parameter('PASSWORD_SECRET_KEY',
                  '',
                  'A string or bytes used for encrypting data. Must be unique '
                  'to the application and long and random enough'),
        Parameter('CHECK_USERNAME', 'lux.extensions.rest:check_username',
                  'Dotted path to username validation function'),
        Parameter('DEFAULT_POLICY', (),
                  'List/tuple of default policy documents'),
        #
        # REST API SETTINGS
        Parameter('API_URL', None, 'URL FOR THE REST API'),
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
                  'Pagination class'),
        Parameter('POST_LOGIN_URL', '',
                  'URL users are redirected to after logging in',
                  jscontext=True),
        Parameter('POST_LOGOUT_URL', None,
                  'URL users are redirected to after logged out',
                  jscontext=True),
        Parameter('WEB_SITE_URL', None,
                  'Url of the website registering to'),
        Parameter('LOGIN_URL', '/login', 'Url to login page', True),
        Parameter('LOGOUT_URL', '/logout', 'Url to logout', True),
        Parameter('REGISTER_URL', '/signup',
                  'Url to register with site', True),
        Parameter('TOS_URL', '/tos',
                  'Terms of Service url',
                  True),
        Parameter('PRIVACY_POLICY_URL', '/privacy-policy',
                  'The url for the privacy policy, required for signups',
                  True),
        #
        Parameter('CORS_ALLOWED_METHODS', 'GET, PUT, POST, DELETE, HEAD',
                  'Access-Control-Allow-Methods for CORS'),
        #
        # SESSIONS
        Parameter('SESSION_COOKIE_NAME', 'LUX',
                  'Name of the cookie which stores session id'),
        Parameter('SESSION_EXCLUDE_URLS', (),
                  'Tuple of urls where persistent session is not required'),
        Parameter('SESSION_EXPIRY', 7 * 24 * 60 * 60,
                  'Expiry for a session/token in seconds.'),
        Parameter('SESSION_BACKEND', None,
                  'Cache backend for session objects.'),
        #
        # CSRF
        Parameter('CSRF_EXPIRY', 60 * 60,
                  'Cross Site Request Forgery token expiry in seconds.'),
        Parameter('CSRF_PARAM', 'authenticity_token',
                  'CSRF parameter name in forms'),
        Parameter('CSRF_BAD_TOKEN_MESSAGE', 'CSRF token missing or incorrect',
                  'Message to display when CSRF is wrong'),
        Parameter('CSRF_EXPIRED_TOKEN_MESSAGE', 'CSRF token expired',
                  'Message to display when CSRF token has expired'),
        #
        #
        Parameter('REGISTER_URL', '/signup',
                  'Url to register with site', True),
        Parameter('RESET_PASSWORD_URL', '/reset-password',
                  'If given, add the router to handle password resets',
                  True),
        Parameter('ACCOUNT_ACTIVATION_DAYS', 2,
                  'Number of days the activation code is valid')
    ]

    def on_config(self, app):
        self.backends = []
        url = app.config['API_URL']
        if url is not None:
            if not is_absolute_uri(url):
                app.config['API_URL'] = str(RestRoot(url))

        if not app.config['PASSWORD_SECRET_KEY']:
            app.config['PASSWORD_SECRET_KEY'] = app.config['SECRET_KEY']

        for dotted_path in app.config['AUTHENTICATION_BACKENDS']:
            backend = module_attribute(dotted_path)
            if not backend:
                self.logger.error('Could not load backend "%s"', dotted_path)
                continue
            backend = backend()
            self.backends.append(backend)
            app.bind_events(backend, exclude=('on_config',))
            if hasattr(backend, 'on_config'):
                backend.on_config(app)

        app.auth_backend = self
        app.providers['Api'] = ApiClient
        app.add_events(('on_before_commit', 'on_after_commit'))

    def sorted_config(self):
        cfg = self.meta.config.copy()
        for backend in self.backends:
            cfg.update(backend.meta.config)
        for key in sorted(cfg):
            yield key, cfg[key]

    def middleware(self, app):
        url = app.config['API_URL']
        middleware = [self]
        for backend in self.backends:
            middleware.extend(backend.middleware(app) or ())

        if url is None:
            return middleware

        self.api_router = RestRoot(url)

        # Add routers and models
        routes = OrderedDict()
        for extension in app.extensions.values():
            api_sections = getattr(extension, 'api_sections', None)
            if api_sections:
                for router in api_sections(app) or ():
                    routes[router.route.path] = router

        # Allow router override
        for router in routes.values():
            if isinstance(router, RestRouter):
                # Register model
                router.model = app.models.register(router.model)
            # Add router to API root-router
            self.api_router.add_child(router)

        # Create the rest-api handler
        app.api = app.providers['Api'](app)

        # routers not required when this is a client app
        if is_absolute_uri(app.config['API_URL']):
            return middleware
        #
        # Create paginator
        dotted_path = app.config['PAGINATION']
        pagination = module_attribute(dotted_path)
        if not pagination:
            raise ImproperlyConfigured('Could not load paginator "%s"',
                                       dotted_path)
        app.pagination = pagination()
        #
        # Add API root-router to middleware
        middleware.append(self.api_router)
        if url != '/':
            # when the api is served by a path, make sure 404 is raised
            # when no suitable routes are found
            middleware.append(
                Rest404(remove_double_slash('%s/<path:path>' % url)))
        #
        # Add the preflight and token events
        events = ('on_preflight', 'on_token')
        app.add_events(events)
        for backend in self.backends:
            app.bind_events(backend, events)

        return middleware

    def response_middleware(self, app):
        middleware = []
        for backend in self.backends:
            middleware.extend(backend.response_middleware(app) or ())
        return middleware

    def api_sections(self, app):
        """Called by this extension to build API middleware
        """
        for backend in self.backends:
            api_sections = getattr(backend, 'api_sections', None)
            if api_sections:
                for router in api_sections(app):
                    yield router

    def __call__(self, environ, start_response):
        return self.request(wsgi_request(environ))
