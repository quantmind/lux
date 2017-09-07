import logging
import json
from contextlib import contextmanager
from collections import OrderedDict
from urllib.parse import urlparse

from pulsar.api import Http404, ImproperlyConfigured
from pulsar.apps.wsgi import Route
from pulsar.utils.httpurl import remove_double_slash
from pulsar.utils.importer import module_attribute

from lux import models

from .rest import RestRoot, RestRouter, Rest404
from .openapi import OpenAPI, ApiPath, api_schema, Specification
from .exc import ErrorMessageSchema, ErrorSchema


LOCAL_API_LOGGER = logging.getLogger('lux.local.api')


class Apis(list, models.Component):
    """Handle one or more server-side or client-side Api
    """
    @classmethod
    def create(cls, app):
        urls = app.config['API_URL']
        if urls is None:
            return
        if isinstance(urls, str):
            urls = [
                {
                    "TITLE": app.config['APP_NAME'],
                    "BASE_PATH": urls
                }
            ]
        elif not isinstance(urls, (list, tuple)):
            urls = [urls]
        return cls().init_app(app).extend(urls)

    def routes(self):
        #
        # Create paginator
        dotted_path = self.config['PAGINATION']
        pagination = module_attribute(dotted_path)
        if not pagination:
            raise ImproperlyConfigured('Could not load paginator "%s"',
                                       dotted_path)
        self.app.pagination = pagination()
        api_routers = OrderedDict()

        # Allow router override
        for extension in self.app.extensions.values():
            api_sections = getattr(extension, 'api_sections', None)
            if api_sections:
                for router in api_sections(self.app) or ():
                    api_routers[router.route.path] = router

        for router in api_routers.values():
            if isinstance(router, RestRouter):
                # Register model
                router.model = self.app.models.register(router.model)
                if router.model:
                    router.model.api_route = router.route
            # Add router to an API
            self.add_child(router)

        for api in self:
            # router not required when api is remote
            if api.netloc:
                continue
            #
            # Add API root-router to middleware
            router = api.router()
            yield router

            url = str(router)
            if url != '/':
                # when the api is served by a path, make sure 404 is raised
                # when no suitable routes are found
                yield Rest404(remove_double_slash('%s/<path:path>' % url))

    def extend(self, iterable):
        for cfg in iterable:
            if not isinstance(cfg, dict):
                self.logger.error('API spec must be a dictionary, got %s', cfg)
                continue
            api = Api.from_cfg(self.app, cfg)
            if api:
                self.append(api)
        return self

    def get(self, path=None):
        """Get the API spec object for a given path
        """
        # allow to pass a route too
        if path and not isinstance(path, str):
            values = dict(((v, v) for v in path.ordered_variables))
            path = path.url(**values)
        #
        if path and path.startswith('/'):
            path = path[1:]
        path = path or ''
        for api in self:
            if api.match(path):
                return api
        raise Http404

    def add_child(self, router):
        parent = self.get(router.route)
        if parent:
            parent.add_child(router)


class Api(models.Component):

    def __init__(self, app, name, spec, spec_path, jwt=None, cors=True):
        self.init_app(app)
        if name == '*':
            name = ''
        self.spec = spec
        self.route = Route('%s/<path:path>' % name)
        self.jwt = jwt
        self.cors = cors
        self.registry = {}
        self._spec_path = spec_path
        self._router = [Specification(spec_path, api=self)]
        self.add_definition(ErrorSchema)
        self.add_definition(ErrorMessageSchema)

    @property
    def spec_path(self):
        """Full path to Api Spec document
        """
        base = self.spec.options['basePath']
        return '%s/%s' % (base, self._spec_path) if base else self._spec_path

    @classmethod
    def from_cfg(cls, app, cfg):
        schema = api_schema.load(cfg)
        if schema.errors:
            app.logger.error('Could not create Api: %s', schema.errors)
            return
        data = api_schema.dump(schema.data).data
        url = urlparse(data['BASE_PATH'])
        schemes = [url.scheme] if url.scheme else None
        spec = OpenAPI(data['TITLE'],
                       version=data['VERSION'],
                       plugins=data['SPEC_PLUGINS'],
                       basePath=url.path,
                       host=url.netloc or None,
                       schemes=schemes,
                       produces=data['PRODUCES'])
        return cls(app, data['MODEL'], spec, data['SPEC_PATH'],
                   cors=data['CORS'])

    def __repr__(self):
        return self.path
    __str__ = __repr__

    @contextmanager
    def ctx(self):
        with self.app.ctx() as ctx:
            ctx.set('api', self)
            try:
                yield ctx
            finally:
                ctx.pop('api')

    @property
    def path(self):
        return self.route.path

    @property
    def netloc(self):
        return self.spec.options['host']

    @property
    def scheme(self):
        schemes = self.spec.options['schemes']
        if schemes:
            return schemes[-1]

    def match(self, path):
        return self.route.match(path)

    def add_child(self, router):
        model = router.model
        if model:
            for schema in model.all_schemas():
                self.add_definition(schema)
        self._router.append(router)

    def router(self):
        if isinstance(self._router, list):
            root = RestRoot(self.spec.options['basePath'])
            for router in self._router:
                root.add_child(self.prepare_router(router))
            self._router = root
            # build the spec so that all lazy operations are done here
            with self.ctx():
                json.dumps(self.spec_dict())
        return self._router

    def prepare_router(self, router):
        api_path = ApiPath(router, cors=self.cors)
        api_path.add_to_spec(self.spec)
        for child in router.routes:
            self.prepare_router(child)
        return router

    def add_definition(self, schema):
        name = models.resource_name(schema)
        if name:
            try:
                self.spec.definition(name, schema=schema)
            except Exception:
                self.app.logger.exception('Could not add spec definition')

    def spec_dict(self):
        return self.spec.to_dict()
