import threading
import json as _json
from io import BytesIO
from urllib.parse import urlparse

from pulsar import Http404
from pulsar.utils.httpurl import parse_options_header
from pulsar.apps.http import JSON_CONTENT_TYPES

from lux.core import raise_http_error


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
            return HttpLocalClient(request, app)
        else:
            http = getattr(self._threads, 'http', None)
            if http is None:
                self._threads.http = http = self.app.http()
            return http

    def __call__(self, request):
        return ApiClientRequest(request, self)

    def request(self, request, method, api, path,
                token=None, headers=None, **kw):
        http = self.http(request, api.netloc)
        url = api.url(path)
        req_headers = []
        req_headers.extend(headers or ())
        agent = request.get('HTTP_USER_AGENT', request.config['APP_NAME'])
        if not token and request.cache.session:
            token = request.cache.session.encoded

        req_headers.append(('user-agent', agent))
        if token:
            req_headers.append(('Authorization', 'Bearer %s' % token))

        response = http.request(method, url, headers=req_headers, **kw)
        raise_http_error(response)
        return response


class ApiClientRequest:
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

    def get(self, path=None, **kw):
        return self.request('GET', path=path, **kw)

    def post(self, path=None, **kw):
        return self.request('POST', path=path, **kw)

    def put(self, path=None, **kw):
        return self.request('PUT', path=path, **kw)

    def head(self, path=None, **kw):
        return self.request('HEAD', path=path, **kw)

    def request(self, method, path=None, **kw):
        if path:
            return self._get(path).request(method, **kw)
        api = self.app.apis.get(self._path)
        return self._api.request(self._request, method, api, self._path, **kw)

    def _get(self, name):
        path = "%s/%s" % (self._path, name) if self._path else name
        return self.__class__(self._request, self._api, path)


class HttpLocalClient:
    """An internal Http client
    """
    def __init__(self, request, app=None):
        self.wsgi_request = request
        self.app = app or request.app

    def request(self, method, url, headers=None, json=None, body=None, **kw):
        environ = self.wsgi_request.environ.copy()
        if environ.get('http.local'):
            raise Http404
        environ.pop('pulsar.cache', None)
        parsed = urlparse(url)
        if headers:
            for header, value in headers:
                if header == "content-type":
                    environ['CONTENT_TYPE'] = value
                elif header == "content-length":
                    environ['CONTENT_LENGTH'] = value
                else:
                    key = 'HTTP_' + header.upper().replace('-', '_')
                    environ[key] = value
        if json:
            body = _json.dumps(json).encode('utf-8')
            environ['CONTENT_TYPE'] = 'application/json; charset=utf-8'

        environ['http.local'] = True
        environ['wsgi.input'] = BytesIO(body or b'')
        environ['REQUEST_METHOD'] = method.upper()
        environ['PATH_INFO'] = parsed.path
        environ['QUERY_STRING'] = parsed.query
        if parsed.netloc:
            environ['HTTP_HOST'] = parsed.netloc
        environ['RAW_URI'] = url
        environ['HTTP_USER_AGENT'] = self.wsgi_request.config['APP_NAME']
        response = self.app(environ, self.start_response)
        return HttpResponse(response)

    def start_response(self, status, response_headers, exc_info=None):
        pass


class HttpResponse:
    """Wrap A WSGI Response object with an API compatible with an HTTP
    response object"""
    __slots__ = ('response',)

    def __init__(self, response):
        self.response = response

    def __repr__(self):
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
        return _json.loads(self.text(charset, errors))

    def decode_content(self):
        '''Return the best possible representation of the response body.
        '''
        ct = self.response.content_type
        if ct:
            ct, _ = parse_options_header(ct)
            if ct in JSON_CONTENT_TYPES:
                return self.json()
            elif ct.startswith('text/'):
                return self.text()
        return self.content
