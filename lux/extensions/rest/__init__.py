from urllib.parse import urljoin
from collections import OrderedDict

from pulsar import ImproperlyConfigured, Http404
from pulsar.utils.importer import module_attribute
from pulsar.utils.httpurl import remove_double_slash

from lux.core import Parameter, LuxExtension

from .models import RestModel, DictModel, RestField, is_rel_field
from .api import Apis
from .api.client import ApiClient, HttpRequestMixin
from .views.rest import RestRouter, MetadataMixin, CRUD, Rest404
from .views.spec import Specification
from .pagination import Pagination, GithubPagination
from .forms import RelationshipField, UniqueField
from .query import Query, RestSession
from .token import TokenBackend, ServiceUser, CORS
from .permissions import user_permissions, validate_policy


__all__ = [
    'RestModel',
    'RestField',
    'is_rel_field',
    'DictModel',
    #
    'RestRouter',
    'MetadataMixin',
    'CRUD',
    'Specification',
    ""
    "ApiClient",
    "HttpRequestMixin",
    #
    'Query',
    'RestSession',
    #
    'Pagination',
    'GithubPagination',
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
    'check_username',
    #
    'validate_policy',
    'user_permissions',
    #
    'TokenBackend',
    'ServiceUser'
]


def api_url(request, location=None):
    try:
        api = request.app.apis.get(location)
        return api.url(location)
    except Http404:
        url = request.absolute_uri('/')
        if location:
            url = urljoin(url, location)
        return url


def api_path(request, model, *args, **params):
    model = request.app.models.get(model)
    if model:
        path = model.api_url(request, **params)
        if path and args:
            path = '%s/%s' % (path, '/'.join((str(s) for s in args)))
        return path


class Extension(LuxExtension):

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
        Parameter('MAX_TOKEN_SESSION_EXPIRY', 7 * 24 * 60 * 60,
                  'Maximum expiry for a token used by a web site in seconds.'),
        #
        Parameter('CORS_ALLOWED_METHODS', 'GET, PUT, POST, DELETE, HEAD',
                  'Access-Control-Allow-Methods for CORS'),
        # TOKENS
        Parameter('JWT_ALGORITHM', 'HS512', 'Signing algorithm')
    ]

    def on_config(self, app):
        app.providers['Api'] = ApiClient
        app.apis = Apis.make(app)
        app.add_events(('on_jwt',
                        'on_query',
                        'on_before_flush',
                        'on_after_flush',
                        'on_before_commit',
                        'on_after_commit'))

    def middleware(self, app):
        # API urls not available - no middleware to add
        if not app.apis:
            return

        middleware = []

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
        has_api = False

        for api in app.apis:

            # router not required when api is remote
            if api.netloc:
                continue

            has_api = True
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
        if has_api:
            app.add_events(('on_preflight', 'on_token'))

        return middleware

    def on_preflight(self, app, request, methods=None):
        '''Preflight handler
        '''
        headers = request.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
        methods = methods or app.config['CORS_ALLOWED_METHODS']
        response = request.response
        origin = request.get('HTTP_ORIGIN', '*')

        if origin == 'null':
            origin = '*'

        response[CORS] = origin
        if headers:
            response['Access-Control-Allow-Headers'] = headers
        if not isinstance(methods, (str, list)):
            methods = list(methods)
        response['Access-Control-Allow-Methods'] = methods
