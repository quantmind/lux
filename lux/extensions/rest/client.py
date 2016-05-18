import threading

from pulsar.utils.httpurl import is_absolute_uri

from lux.core import raise_http_error


class ApiClient:
    '''A python client for a Lux REST Api

    The api can be remote (API_URL is an absolute url) or local (served by
    the same application this client is part of)
    '''
    def __init__(self, app):
        self.app = app
        self._threads = threading.local()
        self._headers = [('content-type', 'application/json')]
        token = app.config['API_AUTHENTICATION_TOKEN']
        if token:
            self._headers.append(('Athentication', 'Bearer %s' % token))

    @property
    def http(self):
        http = getattr(self._threads, 'http', None)
        if http is None:
            self.http = http = self.app.http()
        return http

    @http.setter
    def http(self, value):
        self._threads.http = value

    def __call__(self, request):
        return ApiClientRequest(request, self.http, self._headers)


class ApiClientRequest:
    __slots__ = ('_request', '_http', '_headers')

    def __init__(self, request, http, headers):
        self._request = request
        self._http = http
        self._headers = headers

    @property
    def app(self):
        return self._request.app

    @property
    def url(self):
        url = self._request.config['API_URL']
        if not is_absolute_uri(url):
            path = self._request.path
            if path.startswith(url):
                raise RuntimeError('Cannot access api from API domain')
            url = self._request.absolute_uri(url)
        return url

    def __repr__(self):
        return 'api(%s)' % self.url
    __str__ = __repr__

    def get(self, path, **kw):
        return self.request('GET', path, **kw)

    def post(self, path, **kw):
        return self.request('POST', path, **kw)

    def put(self, path, **kw):
        return self.request('PUT', path, **kw)

    def head(self, path, **kw):
        return self.request('HEAD', path, **kw)

    def request(self, method, path=None, token=None, headers=None, **kw):
        url = self.url
        # Allow to pass an api target dict as path
        if isinstance(path, dict):
            url = path.get('url', url)
            path = path.get('path')
        request = self._request
        url = url_path(url, path)
        req_headers = self._headers[:]
        req_headers.extend(headers or ())
        agent = request.get('HTTP_USER_AGENT', request.config['APP_NAME'])
        if not token and request.cache.session:
            token = request.cache.session.encoded

        req_headers.append(('user-agent', agent))
        if token:
            req_headers.append(('Authorization', 'Bearer %s' % token))

        response = self._http.request(method, url, headers=req_headers, **kw)
        raise_http_error(response)
        return response


def url_path(url, path):
    if path:
        path = str(path)
        if path.startswith('/'):
            path = path[1:]
        if path:
            if not url.endswith('/'):
                url = '%s/' % url
            url = '%s%s' % (url, path)
    return url
