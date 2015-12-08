import json
from urllib.parse import urljoin

from pulsar import new_event_loop
from pulsar.apps.http import HttpClient, JSON_CONTENT_TYPES
from pulsar.utils.httpurl import is_absolute_uri


class ApiClient:
    '''A python client for a Lux Api which can be used by other lux
    applications
    '''
    _http = None
    _wait = None

    def __init__(self, app):
        self.app = app

    def get(self, path, **kw):
        return self.request('GET', path, **kw)

    def post(self, path, **kw):
        return self.request('POST', path, **kw)

    def head(self, path, **kw):
        return self.request('HEAD', path, **kw)

    def request(self, method, path=None, **kw):
        http = self.http()
        url = urljoin(self.app.config['API_URL'], path or '')
        response = http.request(method, url, **kw)
        if self.app.green_pool:
            return self.app.green_pool.wait(response)
        else:
            return response

    def http(self):
        '''Get the HTTP client
        '''
        if self._http is None:
            api_url = self.app.config['API_URL']
            headers = [('content-type', 'application/json')]
            # Remote API
            if is_absolute_uri(api_url):
                if self.app.green_pool:
                    self._http = HttpClient(headers=headers)
                else:
                    self._http = HttpClient(loop=new_event_loop())
            # Local API
            else:
                self._http = LocalClient(self.app, headers)
            token = self.app.config['API_AUTHENTICATION_TOKEN']
            if token:
                self._http.headers['Athentication'] = 'Bearer %s' % token

        return self._http


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

    def get_content(self):
        '''Retrieve the body without flushing'''
        return b''.join(self.response.content)

    def content_string(self, charset=None, errors=None):
        charset = charset or self.response.encoding or 'utf-8'
        return self.get_content().decode(charset, errors or 'strict')

    def json(self):
        return json.loads(self.content_string())

    def decode_content(self):
        '''Return the best possible representation of the response body.
        '''
        ct = self.response.content_type
        if ct:
            if ct in JSON_CONTENT_TYPES:
                return self.json()
            elif ct.startswith('text/'):
                return self.content_string()
        return self.get_content()
