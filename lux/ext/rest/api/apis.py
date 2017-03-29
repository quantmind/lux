import logging
from collections import OrderedDict
from urllib.parse import urlparse, urlunparse

from pulsar.api import Http404, ImproperlyConfigured
from pulsar.apps.wsgi import Route
from pulsar.utils.structures import mapping_iterator
from pulsar.utils.httpurl import remove_double_slash
from pulsar.utils.importer import module_attribute

from lux import models

from apispec import APISpec

from .schema import api_schema
from .rest import RestRoot, RestRouter, Rest404
from .spec import Specification


LOCAL_API_LOGGER = logging.getLogger('lux.local.api')


class Apis(models.Component):
    """Handle one or more server-side or client-side Api
    """
    def __init__(self):
        self._apis = []

    @classmethod
    def create(cls, app):
        urls = app.config['API_URL']
        if urls is None:
            return
        if isinstance(urls, str):
            urls = [
                {
                    "TITLE": app.config['APP_NAME'],
                    "BASE_URL": urls
                }
            ]
        return cls().init_app(app).extend(urls)

    def __repr__(self):
        return repr(self._apis)

    def __iter__(self):
        return iter(self._apis)

    def __len__(self):
        return len(self._apis)

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

        has_api = False
        for api in self:
            # router not required when api is remote
            if api.netloc:
                continue
            if not has_api:
                has_api = True
                self.app.add_events(('on_preflight', 'on_token'))
            #
            # Add API root-router to middleware
            yield api.router
            url = str(api.router)
            if url != '/':
                # when the api is served by a path, make sure 404 is raised
                # when no suitable routes are found
                yield Rest404(remove_double_slash('%s/<path:path>' % url))

    def extend(self, iterable):
        for cfg in mapping_iterator(iterable):
            if not isinstance(cfg, dict):
                self.logger.error('API spec must be a dictionary, got %s', cfg)
                continue
            api = Api.from_cfg(self.app, cfg)
            if api:
                self._apis.append(api)
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
        for api in self._apis:
            if api.match(path):
                return api
        raise Http404

    def add_child(self, router):
        parent = self.get(router.route)
        if parent:
            parent.router.add_child(router)


class Api:
    """Api container
    """
    def __init__(self, app, name, spec, spec_path, jwt=None):
        if name == '*':
            name = ''
        self.spec = spec
        self.route = Route('%s/<path:path>' % name)
        self.jwt = jwt
        self.router = RestRoot(spec.options['basePath'])
        self.router.add_child(Specification(spec_path))

    @classmethod
    def from_cfg(cls, app, cfg):
        schema = api_schema.load(cfg)
        if schema.errors:
            app.logger.error('Could not create Api: %s', schema.errors)
            return
        data = api_schema.dump(schema.data).data
        url = urlparse(data['BASE_URL'])
        schemes = [url.scheme] if url.scheme else None
        spec = APISpec(data['TITLE'],
                       version=data['VERSION'],
                       plugins=data['SPEC_PLUGINS'],
                       basePath=url.path,
                       host=url.netloc,
                       schemes=schemes,
                       produces=data['PRODUCES'])
        return cls(app, data['MODEL'], spec, data['SPEC_PATH'])

    def __repr__(self):
        return self.path
    __str__ = __repr__

    @property
    def path(self):
        return self.route.path

    @property
    def netloc(self):
        return self.spec.options['host']

    def match(self, path):
        return self.route.match(path)

    def url(self, request, path=None):
        urlp = list(self.urlp)
        if path:
            urlp[2] = remove_double_slash('%s/%s' % (urlp[2], str(path)))
        if not urlp[1]:
            r_url = urlparse(request.absolute_uri('/'))
            urlp[0] = r_url.scheme
            urlp[1] = r_url.netloc
        return urlunparse(urlp)
