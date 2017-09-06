import re
import logging
from collections import OrderedDict

from apispec import APISpec, Path
from apispec.utils import load_yaml_from_docstring

from marshmallow import Schema, fields

from lux.core import JsonRouter

from pulsar.apps import wsgi

from .cors import cors


default_plugins = ['apispec.ext.marshmallow']
METHODS = ['get', 'head', 'post', 'put', 'patch', 'delete', 'trace']
RE_URL = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')
LOGGER = logging.getLogger('lux.rest.openapi')


class OpenAPI(APISpec):

    def to_dict(self):
        spec = super().to_dict()
        spec.pop('swagger')
        spec['openapi'] = '3.0.0'
        spec['components'] = dict(
            schemas=spec.pop('definitions'),
            parameters=spec.pop('parameters')
        )
        return spec

    def add_path(self, path=None, operations=None, **kwargs):
        parameters = operations.pop('parameters', None) if operations else None
        if not isinstance(path, Path):
            path = Path(path, operations)
            operations = None
        super().add_path(path=path, operations=operations, **kwargs)
        if parameters:
            self._paths[path.path]['parameters'] = parameters


class APISchema(Schema):
    BASE_URL = fields.String(required=True)
    TITLE = fields.String(required=True)
    VERSION = fields.String(default='0.1.0')
    SPEC_PLUGINS = fields.List(fields.String(), default=default_plugins)
    PRODUCES = fields.List(fields.String(), default=['application/json'])
    SPEC_PATH = fields.String(default='spec',
                              description='path of api specification document')
    MODEL = fields.String(default='*')
    CORS = fields.Boolean(default=True)


api_schema = APISchema()


class ApiOperation:

    def __init__(self, path, method, doc, info):
        self.path = path
        self.method = method
        self.doc = doc if doc is not None else {}
        self.info = info
        self.parameters = []
        self.param_processed = set()

    def add_to_spec(self, spec):
        info = self.info
        if info.path_schema:
            self._extend(spec, info.path_schema, 'path', self.path)
        if info.query:
            self._extend(spec, info.query, 'query')
        if info.form:
            self._extend(spec, info.form, 'formData')
        if isinstance(info.body, as_body):
            info.body(spec, self.doc)

    def _extend(self, spec, schema, loc, entity=None):
        entity = entity or self
        tmp = self._spec(spec)
        tmp.definition('param', schema=schema)
        params = tmp.to_dict()['components']['schemas']['param']
        properties = params['properties']
        required = set(params.get('required') or ())
        for name, obj in properties.items():
            if name in entity.param_processed:
                LOGGER.error(
                    'Parameter "%s" from operation "%s" is already in '
                    'parameter list of "%s"',
                    name, self.method, entity
                )
                continue
            entity.param_processed.add(name)
            obj['name'] = name
            obj['in'] = loc
            if name in required:
                obj['required'] = True
            entity.parameters.append(obj)

    def _spec(self, spec):
        return OpenAPI('', '', plugins=list(spec.plugins))

    def _as_body(self, definition, parameters):
        if not isinstance(definition, dict):
            body = dict(schema={"$ref": "#/definitions/%s" % definition})
        if 'name' not in body:
            body['name'] = 'body'
        body['in'] = 'body'
        body['required'] = True
        parameters.add(body['name'])
        return body


class ApiPath:
    """Utility class for adding a path object to the OpenAPI spec
    
    The path object (dictionary) is extracted from the router
    HTTP methods
    """
    def __init__(self, router, cors=False):
        self.router = router
        self.cors = cors
        self.path = rule2openapi(router.route.rule)
        self.parameters = []
        self.param_processed = set()

    def __repr__(self):
        return self.path

    def __str__(self):
        return self.path

    def add_to_spec(self, spec):
        operations = self.api_operations(spec)
        if not operations:
            return
        path = Path(self.path, operations)
        spec.add_path(path)
        if self.parameters:
            spec._paths[path.path]['parameters'] = self.parameters
        if self.cors:
            self.router.options = cors(
                [method.upper() for method in operations]
            )

    def api_operations(self, spec):
        """Get all API operations for a given path
        
        The path is represented by the router attribute
        
        :param spec: instance of OpenAPI where to add the path info
        """
        operations = OrderedDict()
        for method in METHODS:
            handle = getattr(self.router, method, None)
            if not hasattr(handle, '__call__'):
                continue

            doc = load_yaml_from_docstring(handle.__doc__)
            info = getattr(handle, 'parameters', None)
            if info:
                op = ApiOperation(self, method, doc, info)
                op.add_to_spec(spec)
                doc = op.doc

            if not doc and method == 'head':
                get = operations.get('get')
                if get:
                    doc = get.copy()
                    if 'summary' in doc:
                        doc['summary'] = 'Same as get but does not return body'
                        doc.pop('description', None)
                    else:
                        doc['description'] = (
                            'Same as get but does not return body'
                        )
            operations[method] = doc or {}

        return operations


def rule2openapi(path):
    """Convert a Flask URL rule to an OpenAPI-compliant path.
    :param str path: Flask path template.
    """
    return RE_URL.sub(r'{\1}', path)


class route(wsgi.route):

    def __init__(self, *args, form=None, path_schema=None,
                 query=None, body=None, responses=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api_parameters(
            form=form, path_schema=path_schema,
            query=query, body=body,
            responses=responses
        )

    def __call__(self, method):
        method = super().__call__(method)
        return self.api(method)


class api_parameters:
    """Inject api parameters to an endpoint path or operation
    """
    def __init__(self, form=None, path_schema=None, query=None, body=None,
                 responses=None):
        self.form = form
        self.path_schema = path_schema
        self.query = query
        self.body = body
        self.responses = responses

    def __call__(self, f):
        f.parameters = self
        return f


class as_body:
    """Wrap a Schema so it can be used as a ``requestBody``
    within an Operation Object
    """

    def __init__(self, schema, **obj):
        self.obj = obj
        self.schema_cls = schema if isinstance(schema, type) else type(schema)

    def __call__(self, spec, op):
        definition = None
        plg = spec.plugins.get('apispec.ext.marshmallow')
        if plg and 'refs' in plg:
            definition = plg['refs'].get(self.schema_cls)
        if not definition:
            LOGGER.warning(
                'Could not add body parameter to "%s"', self.schema_cls.__name__
            )
        else:
            op['requestBody'] = {
                "$ref": "#/components/schemas/%s" % definition
            }


class Specification(JsonRouter):
    api = None

    def get(self, request):
        if self.api:
            pass
        spec = self.api.spec_dict()
        spec['servers'] = [
            dict(
                url='%s://%s' % (request.scheme, request.get_host()),
                description="default server"
            )
        ]
        return request.json_response(spec)
