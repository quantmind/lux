import json
from urllib.parse import urljoin

from pulsar import new_event_loop, isawaitable
from pulsar.apps.http import HttpClient, JSON_CONTENT_TYPES
from pulsar.utils.httpurl import is_absolute_uri

from lux import raise_http_error, GreenHttp


class ApiClient:
    '''A python client for a Lux REST Api

    The api can be remote (API_URL is an absolute url) or local (served by
    the same application this client is part of)
    '''
    _http = None
    _headers = None

    def __call__(self, request):
        return ApiClientRequest(request, self.http(request.app),
                                self._headers)

    def http(self, app):
        '''Get the HTTP client
        '''
        if self._http is None:
            api_url = app.config['API_URL']
            self._headers = [('content-type', 'application/json')]
            # Remote API
            if is_absolute_uri(api_url):
                self._http = app.http()
            # Local API
            else:
                self._http = LocalClient(app)
            token = app.config['API_AUTHENTICATION_TOKEN']
            if token:
                self._headers.append(('Athentication', 'Bearer %s' % token))

        return self._http


class ApiClientRequest:

    def __init__(self, request, http, headers):
        self._request = request
        self._http = http
        self._headers = headers

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

    def put(self, path, **kw):
        return self.request('PUT', path, **kw)

    def head(self, path, **kw):
        return self.request('HEAD', path, **kw)

    def request(self, method, path=None, token=None, headers=None, **kw):
        request = self._request
        url = urljoin(self.url, path or '')
        req_headers = self._headers[:]
        req_headers.extend(headers or ())
        agent = request.get('HTTP_USER_AGENT', request.config['APP_NAME'])
        req_headers.append(('user-agent', agent))
        if not token and request.cache.session:
            token = request.cache.session.encoded
        if token:
            req_headers.append(('Authorization', 'Bearer %s' % token))
        response = self._http.request(method, url, headers=req_headers, **kw)
        raise_http_error(response)
        return response


class LocalClient:

    def __init__(self, app):
        self.app = app

    def request(self, method, path, headers=None, **params):
        params['REQUEST_METHOD'] = method.upper()
        request = self.app.wsgi_request(path=path,
                                        headers=headers,
                                        extra=params)
        response = self.app(request.environ, self)
        if self.app.green_pool:
            response = self.app.green_pool.wait(response)
        if isawaitable(response):
            return self._async_response(response)
        else:
            return Response(response)

    async def _async_response(self, response):
        return Response(await response)

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
