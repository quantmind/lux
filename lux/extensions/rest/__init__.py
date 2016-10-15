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
from pulsar.utils.httpurl import remove_double_slash
from pulsar.apps.wsgi import wsgi_request

from lux.core import Parameter

from .auth import AuthBackend, MultiAuthBackend, backend_action
from .models import RestModel, DictModel, RestField, is_rel_field
from .api import Apis
from .api.client import ApiClient, HttpResponse
from .views.actions import (AuthenticationError, check_username, login,
                            logout, user_permissions)
from .views.rest import RestRoot, RestRouter, MetadataMixin, CRUD, Rest404
from .views.auth import Authorization
from .views.spec import Specification
from .pagination import Pagination, GithubPagination
from .forms import RelationshipField, UniqueField
from .query import Query, RestSession
from .user import (MessageMixin, UserMixin, SessionMixin, PasswordMixin,
                   User, Session, session_backend)


__all__ = ['RestModel',
           'RestField',
           'is_rel_field',
           'DictModel',
           #
           'Authorization',
           #
           'AuthBackend',
           'backend_action',
           #
           'RestRouter',
           'MetadataMixin',
           'CRUD',
           ""
           "ApiClient",
           "HttpResponse",
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


def api_path(request, model, *args, **params):
    model = request.app.models.get(model)
    if model:
        path = model.api_url(request, **params)
        if path:
            path = urlparse(path).path
            return '%s/%s' % (path, '/'.join(args)) if args else path


class Extension(MultiAuthBackend):

    _config = [
        Parameter('DEFAULT_POLICY', (),
                  'List/tuple of default policy documents'),
        #
        # REST API SETTINGS
        Parameter('API_URL', None, 'URL FOR THE REST API', True),
        Parameter('API_DOCS_YAML_URL', None,
                  'URL FOR THE REST API YAML DOCS'),
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
        Parameter('PAGINATION', 'lux.extensions.rest.Pagination',
                  'Pagination class'),
        Parameter('WEB_SITE_URL', None,
                  'Url of the website registering to'),
        #
        Parameter('CORS_ALLOWED_METHODS', 'GET, PUT, POST, DELETE, HEAD',
                  'Access-Control-Allow-Methods for CORS'),
        # TOKENS
        Parameter('JWT_ALGORITHM', 'HS512', 'Signing algorithm')
    ]

    def on_config(self, app):
        app.providers['Api'] = ApiClient
        app.apis = Apis.make(app.config['API_URL'])
        app.add_events(('on_before_commit', 'on_after_commit'))

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

        # API urls not available - no middleware to add
        if not app.apis:
            return middleware

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
                if router.model:
                    router.model.api_route = router.route
            # Add router to API root-router
            app.apis.add_child(router)

        # Create the rest-api handler
        app.api = app.providers['Api'](app)

        #
        # Create paginator
        dotted_path = app.config['PAGINATION']
        pagination = module_attribute(dotted_path)
        if not pagination:
            raise ImproperlyConfigured('Could not load paginator "%s"',
                                       dotted_path)
        app.pagination = pagination()

        for api in app.apis:

            # router not required when api is remote
            if api.urlp.netloc:
                continue
            #
            # Add API root-router to middleware
            middleware.append(api.router)
            url = str(api.router)
            if url != '/':
                # when the api is served by a path, make sure 404 is raised
                # when no suitable routes are found
                middleware.append(
                    Rest404(remove_double_slash('%s/<path:path>' % url))
                )
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

    def context(self, request, context):
        """Add user to the Html template context"""
        context['user'] = request.cache.user
