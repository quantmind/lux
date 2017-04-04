from pulsar.apps import wsgi


class route(wsgi.route):

    def __init__(self, *args, responses=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api_parameters(responses=responses)

    def __call__(self, method):
        method = super().__call__(method)
        return self.api(method)


class api_parameters:
    """Inject api parameters to an endpoint handler
    """
    def __init__(self, form=None, path=None, query=None, body=None,
                 responses=None):
        self.form = form
        self.path = path
        self.query = query
        self.body = body
        self.responses = responses

    def __call__(self, f):
        f.parameters = self
        return f

    def add_to(self, pv, doc):
        doc = doc if doc is not None else {}
        parameters = doc.get('parameters', [])
        processed = set()
        if self.path:
            self._extend(pv, self.path, parameters, 'path', processed)
        if self.query:
            self._extend(pv, self.query, parameters, 'query', processed)
        if self.form:
            self._extend(pv, self.form, parameters, 'formData', processed)
        if isinstance(self.body, as_body):
            obj = self.body(pv.spec)
            processed.add(obj['name'])
            parameters.append(obj)
        if parameters:
            doc['parameters'] = parameters
        return doc

    def _extend(self, pv, schema, parameters, loc, processed):
        spec = self._spec(pv)
        spec.definition('param', schema=schema)
        params = spec.to_dict()['definitions']['param']
        properties = params['properties']
        required = set(params.get('required') or ())
        for name, obj in properties.items():
            if name in processed:
                LOG.error('Parameter "%s" already in api path parameter list',
                          name)
                continue
            processed.add(name)
            obj['name'] = name
            obj['in'] = loc
            if name in required:
                obj['required'] = True
            parameters.append(obj)

    def _spec(self, pv):
        return APISpec('', '', plugins=list(pv.spec.plugins))

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
