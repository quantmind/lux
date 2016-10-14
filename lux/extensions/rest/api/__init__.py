from urllib.parse import urlparse, urlunparse

from pulsar import Http404
from pulsar.apps.wsgi import Route
from pulsar.utils.structures import mapping_iterator
from pulsar.utils.httpurl import remove_double_slash

from ..views.rest import RestRoot
from ..views.spec import Specification


class Apis:

    def __init__(self, urls):
        self._apis = []
        self.update(urls)

    @classmethod
    def make(cls, urls):
        if urls is None:
            return
        if isinstance(urls, str):
            urls = (("*", urls),)
        return cls(urls)

    def __repr__(self):
        return repr(self._apis)

    def __iter__(self):
        return iter(self._apis)

    def __len__(self):
        return len(self._apis)

    def update(self, iterable):
        apis = self._apis
        for name, url in mapping_iterator(iterable):
            apis.append(ApiSpec(name, url))
        self._apis = list(reversed(sorted(apis, key=lambda api: api.path)))

    def get(self, path=None):
        if path and path.startswith('/'):
            path = path[1:]
        path = path or ''
        for api in self._apis:
            if api.match(path):
                return api
        raise Http404

    def add_child(self, router):
        values = dict(((v, v) for v in router.route.ordered_variables))
        parent = self.get(router.route.url(**values))
        if parent:
            parent.router.add_child(router)


class ApiSpec:
    """Information about an API
    """
    def __init__(self, name, url, spec=None):
        if name == '*':
            name = ''
        self.route = Route('%s/<path:path>' % name)
        self.urlp = urlparse(url)
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

    def url(self, path):
        urlp = self.urlp
        if path:
            urlp = list(urlp)
            urlp[2] = remove_double_slash('%s/%s' % (urlp[2], str(path)))
        return urlunparse(urlp)
