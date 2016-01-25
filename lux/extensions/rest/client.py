import json
from urllib.parse import urljoin

from pulsar import new_event_loop
from pulsar.apps.http import HttpClient, JSON_CONTENT_TYPES
from pulsar.utils.httpurl import is_absolute_uri

from lux import raise_http_error


class GreenHttp:

    def __init__(self, http, pool):
        self._http = http
        self._pool = pool

    def request(self, method, url, **kw):
        return self._pool.wait(self._http.request(method, url, **kw), True)


class ApiClient:
    '''A python client for a Lux REST Api

    The api can be remote (API_URL is an absolute url) or local (served by
    the same application this client is part of)
    '''
    _http = None

    def __call__(self, request):
        return ApiClientRequest(request, self.http(request.app))

    def http(self, app):
        '''Get the HTTP client
        '''
        if self._http is None:
            api_url = app.config['API_URL']
            headers = [('content-type', 'application/json')]
            # Remote API
            if is_absolute_uri(api_url):
                if app.green_pool:
                    self._http = GreenHttp(HttpClient(headers=headers),
                                           app.green_pool)
                else:
                    self._http = HttpClient(loop=new_event_loop())
            # Local API
            else:
                self._http = LocalClient(app, headers)
            token = app.config['API_AUTHENTICATION_TOKEN']
            if token:
                self._http.headers['Athentication'] = 'Bearer %s' % token

        return self._http


class ApiClientRequest:

    def __init__(self, request, http):
        self._request = request
        self._http = http

    @property
    def url(self):
        return self._request.config['API_URL']

    def __repr__(self):
        return 'api(%s)' % self.url
    __str__ = __repr__

    def get(self, path, **kw):
        return self.request('GET', path, **kw)

    def post(self, path, **kw):
        return self.request('POST', path, **kw)

    def head(self, path, **kw):
        return self.request('HEAD', path, **kw)

    def request(self, method, path=None, token=None, headers=None, **kw):
        request = self._request
        url = urljoin(self.url, path or '')
        req_headers = headers[:] if headers else []
        req_headers.append(('user-agent', request.get('HTTP_USER_AGENT')))
        if not token and request.cache.session:
            token = request.cache.session.encoded
        if token:
            req_headers.append(('Authorization', 'Bearer %s' % token))
        response = self._http.request(method, url, headers=req_headers, **kw)
        raise_http_error(response)
        return response


class LocalClient:

    def __init__(self, app, headers=None):
        self.app = app
        self.headers = headers or []

    def request(self, method, path, **params):
        extra = dict(REQUEST_METHOD=method)
        request = self.app.wsgi_request(path=path,
                                        headers=self.headers,
                                        extra=extra)
        response = yield from self.app(request.environ, self)
        return Response(response)

    def __call__(self, status, response_headers, exc_info=None):
        pass


class Response:
    __slots__ = ('response',)

    def __init__(self, response):
        self.response = response

    def _repr__(self):
        return repr(self.response)

    def __getattr__(self, name):
        return getattr(self.response, name)

    @property
    def content(self):
        '''Retrieve the body without flushing'''
        return b''.join(self.response.content)

    def text(self, charset=None, errors=None):
        charset = charset or self.response.encoding or 'utf-8'
        return self.content.decode(charset, errors or 'strict')

    def json(self, charset=None, errors=None):
        return json.loads(self.text(charset, errors))

    def decode_content(self):
        '''Return the best possible representation of the response body.
        '''
        ct = self.response.content_type
        if ct:
            if ct in JSON_CONTENT_TYPES:
                return self.json()
            elif ct.startswith('text/'):
                return self.text()
        return self.content
