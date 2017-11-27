import re

from lux import openapi
from lux.models import resource_name, get_schema_class

from marshmallow import Schema

from ..utils import load_yaml_from_docstring
from ..core import ApiPath, ApiOperation, METHODS
from .marshmallow import fields2jsonschema, fields2parameters


RE_URL = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')


def setup(spec):
    spec.schema_helpers.append(OpenApiSchema.create)
    spec.parameter_helpers.append(OpenApiSchema.create)
    spec.add_path = AddRouterPath(spec)


class AddRouterPath:

    def __init__(self, spec):
        self.spec = spec

    def __call__(self, router, doc=None, **kwargs):
        doc = doc or {}
        doc.update(load_yaml_from_docstring(router.__doc__) or ())
        path = RouterPath(router, doc)
        path.add_to_spec(self.spec)
        return path


class OpenApiSchema(openapi.OpenApiSchema):

    @classmethod
    def create(cls, schema):
        if isinstance(schema, Schema):
            schema = schema.__class__
        if type(schema) == type(Schema):
            schema = get_schema_class(schema.__name__)()
            return cls(resource_name(schema), schema)

    def __init__(self, name, schema):
        super().__init__(name)
        self._schema = schema

    def schema(self, spec):
        return fields2jsonschema(
            self._schema.fields, self._schema, spec=spec, name=self.name
        )

    def parameters(self, spec, **kw):
        return fields2parameters(
            self._schema.fields, self._schema, spec=spec, name=self.name, **kw
        )


class RouterPath(ApiPath):

    def __init__(self, router, doc=None):
        super().__init__(rule2openapi(router.route.rule), doc=doc)
        self.router = router
        self.model = getattr(router, 'model', None)

    def add_to_spec(self, spec):
        if self.model:
            for schema in self.model.all_schemas():
                spec.add_schema(schema)
        self.get_operations(spec)
        if not self.operations:
            return
        self.doc.update(self.operations)
        self.add('parameters', self.parameters)
        spec.paths[self.path] = self.doc

    def get_operations(self, spec):
        """Get all API operations for a given path

        The path is represented by the router attribute

        :param spec: instance of OpenAPI where to add the path info
        """
        for method in METHODS:
            handle = getattr(self.router, method, None)
            if not hasattr(handle, '__call__'):
                continue

            info = None
            if hasattr(handle, 'rule_method'):
                info = handle.rule_method.parameters.get('openapi')
            doc = load_yaml_from_docstring(handle.__doc__)
            op = ApiOperation(doc, method, extra_info=info)

            if not op.doc and op.method == 'head':
                get = self.operations.get('get')
                if get:
                    doc = get.copy()
                    if 'summary' in doc:
                        doc['summary'] = 'Same as get but does not return body'
                        doc.pop('description', None)
                    else:
                        doc['description'] = (
                            'Same as get but does not return body'
                        )
                    op.doc = doc
                else:
                    continue

            self.operations[method] = op.add_to_path(self, spec)


def rule2openapi(path):
    """Convert a Flask URL rule to an OpenAPI-compliant path.
    :param str path: Flask path template.
    """
    return RE_URL.sub(r'{\1}', path)
