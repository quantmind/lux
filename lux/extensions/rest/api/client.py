import threading

from pulsar import Http401, PermissionDenied
from pulsar.utils.websocket import SUPPORTED_VERSIONS, websocket_key
from pulsar.apps.test import HttpTestClient
from pulsar.apps.greenio import GreenHttp

from lux.core import raise_http_error, app_attribute
from lux.utils.token import encode_json


def app_token(request):
    app = request.app
    payload = {
        'app_name': app.config['APP_NAME'],
        'url': request.absolute_uri('/')[:-1]
    }
    app.fire('on_jwt', request, payload)
    return encode_json(
        payload,
        app.config['SECRET_KEY'],
        algorithm=app.config['JWT_ALGORITHM']
    )


class ApiClient:
    """A python client for interacting with REST APIs"""

    def __init__(self, app):
        self.app = app
        self.local_apps = {}
        self._threads = threading.local()
        self._headers = [('content-type', 'application/json')]

    def http(self, request, netloc=None):
        app = self.local_apps.get(netloc) if netloc else self.app
        if app:
            return http_local(app)
        else:
            http = getattr(self._threads, 'http', None)
            if http is None:
                self._threads.http = http = self.app.http()
            return http

    def __call__(self, request):
        return ApiClientRequest(request, self)

    def request(self, request, method, api, path,
                token=None, jwt=False, headers=None, auth_error=None, **kw):
        http = self.http(request, api.netloc)
        url = api.url(request, path)
        req_headers = []
        req_headers.extend(headers or ())
        agent = request.get('HTTP_USER_AGENT', request.config['APP_NAME'])
        req_headers.append(('user-agent', agent))

        if jwt:
            jwt = app_token(request)
            req_headers.append(('Authorization', 'JWT %s' % jwt))
        else:
            if not token and request.cache.session:
                token = request.cache.session.token
            if token:
                req_headers.append(('Authorization', 'Bearer %s' % token))

        response = http.request(method, url, headers=req_headers, **kw)
        try:
            raise_http_error(response, method, url)
        except (Http401, PermissionDenied) as exc:
            request.logger.error(str(exc))
            if auth_error:
                raise auth_error from None
            raise
        return response


class HttpRequestMixin:

    def delete(self, path=None, **kw):
        return self.request('DELETE', path=path, **kw)

    def get(self, path=None, **kw):
        return self.request('GET', path=path, **kw)

    def head(self, path=None, **kw):
        return self.request('HEAD', path=path, **kw)

    def options(self, path=None, **extra):
        return self.request('OPTIONS', path, **extra)

    def patch(self, path=None, **kw):
        return self.request('PATCH', path=path, **kw)

    def post(self, path=None, **kw):
        return self.request('POST', path=path, **kw)

    def put(self, path=None, **kw):
        return self.request('PUT', path=path, **kw)

    def wsget(self, path=None, headers=None, **kw):
        """make a websocket request"""
        if headers is None:
            headers = []
        headers.extend((
            ('Connection', 'Upgrade'),
            ('Upgrade', 'websocket'),
            ('Sec-WebSocket-Version', str(max(SUPPORTED_VERSIONS))),
            ('Sec-WebSocket-Key', websocket_key())
        ))
        return self.request('GET', path=path, headers=headers, **kw)

    def request(self, method, path=None, **kw):
        raise NotImplementedError


class ApiClientRequest(HttpRequestMixin):
    __slots__ = ('_request', '_api', '_path')

    def __init__(self, request, api, path=None):
        self._request = request
        self._api = api
        self._path = path

    def __getattr__(self, name):
        return self._get(name)

    def __getitem__(self, name):
        return self._get(name)

    @property
    def app(self):
        return self._request.app

    def __repr__(self):
        return 'api(%s)' % self.url
    __str__ = __repr__

    def request(self, method, path=None, **kw):
        if path:
            return self._get(path).request(method, **kw)
        api = self.app.apis.get(self._path)
        return self._api.request(self._request, method, api, self._path, **kw)

    def _get(self, name):
        path = "%s/%s" % (self._path, name) if self._path else name
        return self.__class__(self._request, self._api, path)


@app_attribute
def http_local(app):
    http = HttpTestClient(app.callable, app, headers={'X-Http-Local': 'local'})
    return GreenHttp(http)
