import logging

from urllib.parse import urlparse, urlunparse

from pulsar import Http404
from pulsar.apps.wsgi import Route
from pulsar.utils.structures import mapping_iterator
from pulsar.utils.httpurl import remove_double_slash

from lux.core import AppComponent

from ..views.rest import RestRoot

from ..views.spec import Specification


LOCAL_API_LOGGER = logging.getLogger('lux.local.api')


class Apis(AppComponent):

    def __init__(self, app, urls):
        super().__init__(app)
        self._apis = []
        self.update(urls)

    @classmethod
    def make(cls, app):
        urls = app.config['API_URL']
        if urls is None:
            return
        if isinstance(urls, str):
            urls = (("*", urls),)
        return cls(app, urls)

    def __repr__(self):
        return repr(self._apis)

    def __iter__(self):
        return iter(self._apis)

    def __len__(self):
        return len(self._apis)

    def update(self, iterable):
        apis = self._apis
        for name, cfg in mapping_iterator(iterable):
            if isinstance(cfg, str):
                cfg = {'url': cfg}
            apis.append(ApiSpec(self.app, name, **cfg))
        self._apis = list(reversed(sorted(apis, key=lambda api: api.path)))

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


class ApiSpec:
    """Information about an API
    """
    def __init__(self, app, name, url=None, jwt=None, spec=None):
        if name == '*':
            name = ''
        self.route = Route('%s/<path:path>' % name)
        self.urlp = urlparse(url)
        self.jwt = jwt
        self.spec = spec
        self.router = RestRoot(self.urlp.path)
        if spec:
            self.router.add_child(Specification(spec))

    def __repr__(self):
        return self.path
    __str__ = __repr__

    @property
    def path(self):
        return self.route.path

    @property
    def netloc(self):
        return self.urlp.netloc

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
