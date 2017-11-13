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
from lux.openapi import OpenAPI

from .openapi import api_schema, Specification
from .rest import RestRoot, RestRouter, Rest404
from .exc import ErrorMessageSchema, ErrorSchema
from .cors import cors


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
    """An Api is a set of OpenAPI paths under a base Url
    """
    def __init__(self, app, name, spec, spec_path, url, jwt=None, cors=True):
        self.init_app(app)
        if name == '*':
            name = ''
        self.spec = spec
        self.route = Route('%s/<path:path>' % name)
        self.url = url
        self.jwt = jwt
        self.cors = cors
        self.registry = {}
        self._spec_path = spec_path
        self._router = [Specification(spec_path, api=self)]
        self.spec.add_schema(ErrorSchema)
        self.spec.add_schema(ErrorMessageSchema)

    @property
    def spec_path(self):
        """Full path to Api Spec document
        """
        return (
            '%s/%s' % (self.url.path, self._spec_path) if self.url.path
            else self._spec_path
        )

    @classmethod
    def from_cfg(cls, app, cfg):
        schema = api_schema.load(cfg)
        if schema.errors:
            app.logger.error('Could not create Api: %s', schema.errors)
            return
        data = api_schema.dump(schema.data).data
        url = urlparse(data['BASE_PATH'])
        spec = OpenAPI(
            data['TITLE'],
            version=data['VERSION'],
            info=dict(description=data.get('DESCRIPTION', '')),
            plugins=data['SPEC_PLUGINS'],
            default_responses=app.config['DEFAULT_REST_RESPONSES']
        )
        return cls(app, data['MODEL'], spec, data['SPEC_PATH'], url,
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
        return self.spec.doc.get('host')

    @property
    def scheme(self):
        schemes = self.spec.doc.get('schemes')
        if schemes:
            return schemes[-1]

    def match(self, path):
        return self.route.match(path)

    def add_child(self, router):
        assert isinstance(self._router, list), 'Cannot add child'
        self._router.append(router)

    def router(self):
        """Return the base router of this API.
        
        If the base router is not available it first builds the paths and
        subsequently returns it
        """
        if isinstance(self._router, list):
            # base router
            with self.ctx():
                root = RestRoot(self.url.path)
                for router in self._router:
                    root.add_child(self._prepare_router(router))
                self._router = root
                # build the spec so that all lazy operations are done here
                json.dumps(self.spec_dict())
        return self._router

    def spec_dict(self):
        return self.spec.to_dict()

    # INTERNALS

    def _prepare_router(self, router):
        path = self.spec.add_path(router)
        #
        # inject api spec in the router
        router.api_spec = self.spec
        #
        # add CORS route to the router
        if self.cors:
            router.options = cors(
                [method.upper() for method in path.operations]
            )
        for child in router.routes:
            self._prepare_router(child)
        return router
