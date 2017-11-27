import logging
from collections import OrderedDict

from .utils import compact

METHODS = ['get', 'head', 'post', 'put', 'patch', 'delete', 'trace']

LOGGER = logging.getLogger('lux.rest.openapi')


class OpenAPIError(Exception):
    """Base class for all apispec-related errors."""
    pass


class PluginError(OpenAPIError):
    """Raised when a plugin cannot be found or is invalid."""
    pass


class OperationInfo:

    def __init__(self,
                 path=None,
                 body=None,
                 query=None,
                 header=None,
                 responses=None,
                 default_response=200,
                 default_response_schema=None):
        self.path = path
        self.body = body
        self.query = query
        self.header = header
        self.default_response = default_response
        self.responses = dict()
        self.responses[default_response] = default_response_schema
        if isinstance(responses, dict):
            self.responses.update(responses)
        elif responses:
            self.responses.update(((r, None) for r in responses))

    @property
    def schema(self):
        schema = self.responses[self.default_response]
        if isinstance(schema, list):
            schema = schema[0]
        return schema


class OpenApiSchema:

    def __init__(self, name):
        self.name = name

    def schema(self):
        """Convert the schema into a valid OpenApi Json schema object
        """
        raise NotImplementedError

    def parameters(self, **kwargs):
        """Convert the schema into a valid OpenApi Parameters map
        """
        raise NotImplementedError


class OpenAPIbase:

    def __init__(self, doc=None):
        self.doc = doc or {}
        self.parameters = {}
        self.servers = []
        self._name_loc = {}
        self.tags = dict(tag_generator(self.doc.pop('tags', None)))

    def add(self, key, value):
        if value:
            self.doc[key] = value

    def add_parameters(self, schema, spec=None, **kw):
        """Add parameters from a schema object
        """
        if not schema:
            return
        spec = spec or self
        for func in spec.schema_helpers:
            schema = func(schema) or schema

        if isinstance(schema, OpenApiSchema):
            for param in schema.parameters(spec, **kw):
                name = param['name']
                loc = param['in']
                key = (loc, name)
                if key in self._name_loc:
                    LOGGER.error('parameter %s already in %s', name, loc)
                else:
                    self._name_loc[key] = True
                    if name in self.parameters:
                        name = '%s%s' % (name, loc)
                    self.parameters[name] = param
        else:
            raise PluginError(
                'Could not find a valid plugin to convert a schema to '
                'an OpenAPI schema'
            )

    def add_server(self, url, description=None):
        """Add a server object to this Api Object
        """
        self.servers.append(compact(url=url, description=description))


class OpenAPI(OpenAPIbase):
    """Open API v 3.0 document builder
    """
    version = '3.0.0'

    def __init__(self, title, version, info=None, plugins=(),
                 default_content_type=None, default_responses=None,
                 **options):
        super().__init__(options)
        self.doc.update(
            openapi=self.version,
            info=dict(title=title, version=version),
            paths=OrderedDict()
        )
        self.doc['info'].update(info or {})
        # Metadata
        self.schemas = {}
        self.parameters = {}
        self.responses = {}
        self.tags = OrderedDict()
        self.plugins = {}
        self.default_content_type = default_content_type or 'application/json'
        self.default_responses = default_responses or {}
        #
        self.parameter_helpers = []
        self.schema_helpers = []
        for plugin_path in plugins:
            self.setup_plugin(plugin_path)

    def __repr__(self):
        return '%s %s' % (self.__class__.__name__, self.version)

    @property
    def paths(self):
        return self.doc['paths']

    def to_dict(self):
        s = self.schemas
        p = self.parameters
        r = self.responses
        ret = self.doc.copy()
        ret.update(compact(
            tags=[self.tags[name] for name in sorted(self.tags)],
            components=compact(
                schemas=OrderedDict(((k, s[k]) for k in sorted(s))),
                parameters=OrderedDict(((k, p[k]) for k in sorted(p))),
                responses=OrderedDict(((k, r[k]) for k in sorted(r))),
            ),
            servers=self.servers
        ))
        return ret

    # adapted from Sphinx
    def setup_plugin(self, path):
        """Import and setup a plugin. No-op if called twice
        for the same plugin.
        :param str path: Import path to the plugin.
        :raise: PluginError if the given plugin is invalid.
        """
        if path in self.plugins:
            return
        try:
            mod = __import__(
                path, globals=None, locals=None, fromlist=('setup',)
            )
        except ImportError as err:
            raise PluginError(
                'Could not import plugin "{0}"\n\n{1}'.format(path, err)
            )
        if not hasattr(mod, 'setup'):
            raise PluginError(
                'Plugin "{0}" has no setup(spec) function'.format(path))
        else:
            # Each plugin gets a dict to store arbitrary data
            self.plugins[path] = {}
            mod.setup(self)
        return None

    def add_path(self, router, **kwargs):
        path = ApiPath(router, **kwargs)
        path.add_to_spec(self)

    def add_schema(self, schema):
        """Add a schema to the schema mapping in component
        """
        for func in self.schema_helpers:
            schema = func(schema) or schema

        if isinstance(schema, OpenApiSchema):
            if schema.name not in self.schemas:
                self.schemas[schema.name] = schema.schema(self)
            return {'$ref': '#/components/schemas/%s' % schema.name}
        elif schema:
            LOGGER.error(
                'Could not find a valid plugin to convert %r to '
                'an OpenAPI schema', schema
            )

    def schema2parameters(self, schema, **kw):
        for func in self.parameter_helpers:
            schema = func(schema) or schema

        if isinstance(schema, OpenApiSchema):
            return schema.parameters(self, **kw)
        else:
            raise PluginError(
                'Could not find a valid plugin to convert schema to '
                'OpenAPI parameters'
            )


class ApiPath(OpenAPIbase):
    """Utility class for adding a path object to the OpenAPI spec

    The path object (dictionary) is extracted from the router
    HTTP methods
    """
    def __init__(self, path, doc=None):
        super().__init__(doc)
        self.path = path
        self.operations = OrderedDict()

    def __repr__(self):
        return self.path

    def add_to_spec(self, spec):
        spec.doc['paths'][self.path] = self.doc


class ApiOperation(OpenAPIbase):
    """Utility class for adding an operation to an API Path
    """
    def __init__(self, doc, method, extra_info=None):
        super().__init__(doc)
        self.method = method
        self.info = extra_info

    def __repr__(self):
        return self.method

    def add_to_path(self, path, spec):
        info = self.info
        self.tags.update(path.tags)
        self.add('tags', sorted(self.tags))
        spec.tags.update(self.tags)
        if info:
            self.add_parameters(info.path, spec, location='path')
            self.add_parameters(info.query, spec, location='query')
            self.add_parameters(info.header, spec, location='header')
            self.add_body(info.body, spec)
        self.add_responses(path, spec)
        p = self.parameters
        self.add('parameters', [p[k] for k in sorted(p)])
        return self.doc

    def add_body(self, schema, spec):
        if not schema:
            return
        body = self.doc.get('requestBody')
        if not body:
            self.doc['requestBody'] = body = dict()
        self.add_content_schema(schema, body, spec)

    def add_responses(self, path, spec):
        info = self.info
        responses = self.doc.get('responses', None) or {}
        if info:
            defaults = spec.default_responses
            all_responses = {}
            for code, cfg in info.responses.items():
                doc = {}
                doc.update(defaults.get(code) or ())
                try:
                    doc.update(responses.get(code) or ())
                except ValueError as exc:
                    LOGGER.error(
                        "Cannot updated '%s %s' response '%s' with "
                        "doc string %r, a dictionary is expected",
                        self, path, code, responses[code]
                    )
                schema = doc.pop('schema', None)
                self.add_content_schema(cfg or schema, doc, spec)
                all_responses[code] = doc
            responses = all_responses
        self.doc['responses'] = OrderedDict(
            ((code, responses[code]) for code in responses)
        )

    def add_content_schema(self, schema, doc, spec, content_type=None):
        is_array = False
        if isinstance(schema, list) and len(schema) == 1:
            is_array = True
            schema = schema[0]
        if not isinstance(schema, str):
            schema = spec.add_schema(schema)
        if not schema:
            return
        if 'content' not in doc:
            doc['content'] = {}
        content = doc['content']
        if not content_type:
            content_type = spec.default_content_type

        if is_array:
            content[content_type] = dict(
                schema=dict(type='array', items=schema)
            )
        else:
            content[content_type] = dict(schema=schema)


def tag_generator(tags):
    for tag in (tags or ()):
        if isinstance(tag, str):
            tag = dict(name=tag)
        yield tag['name'], tag
