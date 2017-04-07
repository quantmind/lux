from urllib.parse import urljoin

from pulsar.api import Http404

from lux.core import Parameter, LuxExtension

from .api import (
    Apis, RestRouter, Pagination, GithubPagination,
    route, api_parameters
)
from .api.client import ApiClient, HttpRequestMixin
from .token import TokenBackend, ServiceUser
from .permissions import PolicySchema, user_permissions, validate_policy
from .query import DictModel


__all__ = [
    'RestRouter',
    'MetadataMixin',
    'Specification',
    "ApiClient",
    "HttpRequestMixin",
    #
    'DictModel',
    #
    'Pagination',
    'GithubPagination',
    #
    'api_url',
    'api_path',
    #
    'login',
    'logout',
    'check_username',
    #
    'PolicySchema',
    'validate_policy',
    'user_permissions',
    #
    'TokenBackend',
    'ServiceUser',
    #
    # OpenAPI
    'route',
    'api_parameters'
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
        # OPEN API SPEC SETTINGS
        Parameter('API_TITLE', None,
                  'Open API title, if not set the openapi spec wont be '
                  'created'),
        Parameter('API_SPEC_PLUGINS', ['apispec.ext.marshmallow',
                                       'lux.extensions.rest.openapi'],
                  'Open API spec extensions'),
        #
        # REST API SETTINGS
        Parameter('API_URL', None, 'List of API specifications', True),
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
        Parameter('PAGINATION', 'lux.ext.rest.Pagination',
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
        app.apis = Apis.create(app)
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
        # Create the api client and return api routes
        app.api = app.providers['Api'](app)
        return app.apis.routes()
