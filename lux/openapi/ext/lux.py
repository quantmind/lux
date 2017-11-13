import re

from ..utils import load_yaml_from_docstring
from ..core import ApiPath, ApiOperation, METHODS


RE_URL = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')


def setup(openapi):
    helper = LuxOpenApi(openapi)
    openapi.add_path = helper.add_path


class LuxOpenApi:

    def __init__(self, openapi):
        self.openapi = openapi
        self._add_path = openapi.add_path

    def add_path(self, router, doc=None, **kwargs):
        doc = doc or {}
        doc.update(load_yaml_from_docstring(router.__doc__) or ())
        path = RouterPath(router, doc)
        path.add_to_spec(self.openapi)
        return path


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

            self.operations[method] = op.add_to_path(self, spec)


def rule2openapi(path):
    """Convert a Flask URL rule to an OpenAPI-compliant path.
    :param str path: Flask path template.
    """
    return RE_URL.sub(r'{\1}', path)

