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
from importlib import import_module
from urllib.parse import urljoin

from pulsar import ImproperlyConfigured
from pulsar.utils.importer import module_attribute
from pulsar.utils.httpurl import is_absolute_uri

from lux.core import Parameter
from lux.core.wrappers import wsgi_request

from .user import *             # noqa
from .auth import *             # noqa
from .models import *           # noqa
from .pagination import *       # noqa
from .client import ApiClient
from .views import *            # noqa
from .authviews import *        # noqa
from .ws import WsModelRpc
from .policy import has_permission


def luxrest(url, **rest):
    """Dictionary containing the api type and the api url name
    """
    rest['url'] = url
    return rest


def website_url(request, location=None):
    """A website url
    """
    url = request.config.get('WEB_SITE_URL')
    url = url or request.absolute_uri('/')
    if location:
        url = urljoin(url, location)
    return url


class Extension(MultiAuthBackend, WsModelRpc):

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
        Parameter('SECRET_KEY',
                  'secret-key',
                  'A string or bytes used for encrypting data. Must be unique '
                  'to the application and long and random enough'),
        Parameter('SESSION_EXPIRY', 7*24*60*60,
                  'Expiry for a session/token in seconds.'),
        Parameter('CHECK_USERNAME', check_username,
                  'Check if the username is valid'),
        Parameter('PERMISSION_LEVELS', {'read': 10,
                                        'create': 20,
                                        'update': 30,
                                        'delete': 40},
                  'When a model'),
        Parameter('DEFAULT_PERMISSION_LEVEL', 'read',
                  'Default permission level'),
        Parameter('DEFAULT_PERMISSION_LEVELS', {'site:admin': 'none'},
                  'Dictionary of default permission levels'),
        Parameter('API_URL', None, 'URL FOR THE REST API', True),
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
                  'Url of the website registering to')]

    def on_config(self, app):
        self.backends = []
        app.rest_api_client = False
        url = app.config['API_URL']
        if url is not None:
            if is_absolute_uri(url):
                app.rest_api_client = True
            else:
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

    def sorted_config(self):
        cfg = self.meta.config.copy()
        for backend in self.backends:
            cfg.update(backend.meta.config)
        for key in sorted(cfg):
            yield key, cfg[key]

    def middleware(self, app):
        middleware = [self]
        for backend in self.backends:
            middleware.extend(backend.middleware(app) or ())

        dotted_path = app.config['PAGINATION']
        pagination = module_attribute(dotted_path)
        if not pagination:
            raise ImproperlyConfigured('Could not load paginator "%s"',
                                       dotted_path)
        app.pagination = pagination()

        url = app.config['API_URL']
        # If the api url is not absolute, add the api middleware
        if url is not None:
            if is_absolute_uri(url):
                app.api = ApiClient(app)
            else:
                # Add the preflight and token events
                events = ('on_preflight', 'on_token')
                app.add_events(events)
                for backend in self.backends:
                    app.bind_events(backend, events)

                api = RestRoot(url)
                middleware.append(api)
                for extension in app.extensions.values():
                    api_sections = getattr(extension, 'api_sections', None)
                    if api_sections:
                        for router in api_sections(app):
                            if not isinstance(router, ModelMixin):
                                raise ImproperlyConfigured('Router must be a '
                                                           'ModelMixin')
                            # Register model
                            router.model = app.models.register(router.model)
                            # Add router
                            api.add_child(router)

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


class SimpleBackend(AuthBackend):

    def has_permission(self, request, resource, action):
        return has_permission(request, {}, resource, action)
