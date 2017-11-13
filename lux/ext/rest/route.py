from functools import wraps

from pulsar.api import ImproperlyConfigured
from pulsar.apps import wsgi

from lux.models import Schema
from lux.openapi import OperationInfo
from lux.openapi.ext.marshmallow import resource_name
from lux.utils.data import compact_dict


class route(wsgi.route):
    """Extend pulsar wsgi route decorator for openapi information
    
    It adds the openapi namedtuple to the route parameters dictionary
    """
    def __init__(self, rule=None, body_schema=None, path_schema=None,
                 query_schema=None, header_schema=None, default_response=200,
                 default_response_schema=None,
                 responses=None, **kwargs):
        if isinstance(rule, type(Schema)):
            rule = rule()
        if isinstance(rule, Schema):
            if path_schema:
                raise ImproperlyConfigured(
                    'both rule and path_schema are provided as schema'
                )
            path_schema = rule
            rule = path_schema.rule()
        kwargs['openapi'] = OperationInfo(
            path=path_schema,
            body=body_schema,
            query=query_schema,
            header=header_schema,
            responses=responses,
            default_response=default_response,
            default_response_schema=default_response_schema
        )
        super().__init__(rule, **kwargs)

    def __call__(self, method):
        api = self.parameters['openapi']

        if api.body or api.responses[api.default_response]:

            # the callable must accept the schema as second parameter
            @wraps(method)
            def _(router, request):
                schemas = router.api_spec.schemas
                return method(router, request, **compact_dict(
                    body_schema=schemas.get(resource_name(api.body)),
                    query_schema=schemas.get(resource_name(api.query)),
                    schema=schemas.get(resource_name(api.body))
                ))

            return super().__call__(_)

        return super().__call__(method)
