import re

from apispec import APISpec
from apispec.utils import load_yaml_from_docstring

from marshmallow import Schema, fields

from lux.core import JsonRouter

from pulsar.apps import wsgi


default_plugins = ['apispec.ext.marshmallow']
METHODS = ['get', 'head', 'post', 'put', 'patch', 'delete', 'trace']


class APISchema(Schema):
    BASE_URL = fields.String(required=True)
    TITLE = fields.String(required=True)
    VERSION = fields.String(default='0.1.0')
    SPEC_PLUGINS = fields.List(fields.String(), default=default_plugins)
    PRODUCES = fields.List(fields.String(), default=['application/json'])
    SPEC_PATH = fields.String(default='spec')
    MODEL = fields.String(default='*')
    CORS = fields.Boolean(default=True)


api_schema = APISchema()
RE_URL = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')


def api_operations(api, router):
    """Get all API operations"""
    operations = {}
    for method in METHODS:
        handle = getattr(router, method, None)
        if not hasattr(handle, '__call__'):
            continue

        doc = load_yaml_from_docstring(handle.__doc__)
        parameters = getattr(handle, 'parameters', None)
        if parameters:
            doc = parameters.add_to(api, doc)
        if not doc and method == 'head':
            get = operations.get('get')
            if get:
                doc = get.copy()
                if 'summary' in doc:
                    doc['summary'] = 'Same as get but does not return body'
                    doc.pop('description', None)
                else:
                    doc['description'] = 'Same as get but does not return body'
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
    """Inject api parameters to an endpoint handler
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

    def add_to(self, api, doc):
        doc = doc if doc is not None else {}
        parameters = doc.get('parameters', [])
        processed = set()
        if self.path_schema:
            self._extend(api, self.path_schema, parameters, 'path', processed)
        if self.query:
            self._extend(api, self.query, parameters, 'query', processed)
        if self.form:
            self._extend(api, self.form, parameters, 'formData', processed)
        if isinstance(self.body, as_body):
            obj = self.body(api.spec)
            processed.add(obj['name'])
            parameters.append(obj)
        if parameters:
            doc['parameters'] = parameters
        return doc

    def _extend(self, api, schema, parameters, loc, processed):
        spec = self._spec(api)
        spec.definition('param', schema=schema)
        params = spec.to_dict()['definitions']['param']
        properties = params['properties']
        required = set(params.get('required') or ())
        for name, obj in properties.items():
            if name in processed:
                api.logger.error(
                    'Parameter "%s" already in api path parameter list', name
                )
                continue
            processed.add(name)
            obj['name'] = name
            obj['in'] = loc
            if name in required:
                obj['required'] = True
            parameters.append(obj)

    def _spec(self, api):
        return APISpec('', '', plugins=list(api.spec.plugins))

    def _as_body(self, definition, parameters):
        if not isinstance(definition, dict):
            body = dict(schema={"$ref": "#/definitions/%s" % definition})
        if 'name' not in body:
            body['name'] = 'body'
        body['in'] = 'body'
        body['required'] = True
        parameters.add(body['name'])
        return body


class as_body:

    def __init__(self, schema, **obj):
        self.obj = obj
        self.schema_cls = schema if isinstance(schema, type) else type(schema)

    def __call__(self, spec):
        definition = None
        plg = spec.plugins.get('apispec.ext.marshmallow')
        if plg and 'refs' in plg:
            definition = plg['refs'].get(self.schema_cls)
        if not definition:
            LOG.warning('Could not add body parameter %s' % self.schema_cls)
        else:
            obj = self.obj.copy()
            obj['schema'] = {"$ref": "#/definitions/%s" % definition}
            obj['in'] = 'body'
            if 'name' not in obj:
                obj['name'] = definition.lower()
            return obj


class Specification(JsonRouter):
    api = None

    def get(self, request):
        if self.api:
            pass
        spec = self.api.spec_dict()
        if not spec.get('host'):
            spec['host'] = request.get_host()
        if not spec.get('schemes'):
            spec['schemes'] = [request.scheme]
        return request.json_response(spec)
