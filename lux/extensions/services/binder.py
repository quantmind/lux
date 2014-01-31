'''
api_function
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: api_function
   :members:
   :member-order: bysource

API
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: API
   :members:
   :member-order: bysource
'''
import json

from pulsar.apps.http import HttpClient, Auth
from pulsar.utils.httpurl import appendslash, is_succesful, urlparse
from pulsar.utils.tools import nice_number

__all__ = ['api_function', 'API', 'APIS']


class ApiFunctionNotAvailable(AttributeError):
    '''Exception raised when requesting an API function which
is not available'''
    def __init__(self, api, name):
        self.msg = '%s has no api function "%s"' % (api, name)
        super(ApiFunctionNotAvailable, self).__init__(msg)


class api_function(object):
    '''Bind an API function to an API.

.. attribute:: name

    This attribute is set at runtime by the :class:`API` metaclass.

    It is the declarative name of this :class:`api_function` in a :class:`API`
    class.

.. attribute:: path

    Relative or absolute url of api function.

    If a relative url, the full url is constructed by prepending the
    the :attr:`API.BASE_URL`

.. attribute:: nargs

    Number of required arguments used to form the final url. It the
    value is set to "*", the number can vary and no check is performed.

.. attribute:: required_params

    Tuple of parameter names required (not optional) by the api call.

    Can be ``None``.

.. attribute:: http_params

    Additional parameters to pass to the http request method.
'''
    name = None

    def __init__(self, path=None, nargs=0, allowed_params=None,
                 required_params=None, callback=None, method=None,
                 append=None, doc=None, **http_params):
        self.path = path or ''
        self.scheme = urlparse(path).scheme
        self.nargs = nargs
        self.append = append
        self.required_params = required_params or []
        self.doc = doc
        self.callback = callback
        self.http_params = http_params
        self.method = (method or 'get').upper()
        if self.required_params and not allowed_params:
            allowed_params = dict(((p, None) for p in self.required_params))
        self.allowed_params = allowed_params or {}

    def __repr__(self):
        if self.path:
            return '%s (%s %s)' % (self.name, self.method, self.path)
        else:
            return '%s (%s)' % (self.name, self.method)
    __str__ = __repr__

    def __get__(self, api, instance_type=None):
        if api:
            return apicall(api, self)
        else:
            raise ValueError()

    def check_params(self, params):
        http_extra = self.http_params.copy()
        for p in list(params):
            if p not in self.allowed_params:
                http_extra[p] = params.pop(p)
        for p in self.allowed_params:
            if p not in params:
                v = self.allowed_params[p]
                if v:
                    params[p] = v
        if self.required_params:
            rp = list(self.required_params)
            for p in params:
                try:
                    rp.remove(p)
                except ValueError:
                    continue
            if rp:
                raise TypeError("%s() requires keyword argument '%s'" %
                                (self.name, rp[0]))
        return params, http_extra


class apicall(object):
    __slots__ = ('api', 'call')

    def __init__(self, api, call):
        self.api = api
        self.call = call

    def __str__(self):
        return '%s.%s' % (self.api, self.call)
    __repr__ = __str__

    def __call__(self, *args, **kwargs):
        call = self.call
        if call.nargs != '*' and len(args) != call.nargs:
            raise TypeError('%s() takes exactly %s (%s given)' %
                            (call.name,
                             nice_number(call.nargs, 'argument'),
                             nice_number(len(args))))
        url = call.path
        params, http_extra = call.check_params(kwargs)
        if args:
            url = appendslash(url) + '/'.join(('%s' % a for a in args))
        if call.append:
            url = appendslash(url) + call.append
        if not call.scheme:
            url = self.api.BASE_URL + url
        response = self.api.request(call, url, params, **http_extra)
        return response.on_finished.add_callback(self.callback)

    def callback(self, response):
        result = self.api.handle_response(self.call, response)
        if self.call.callback:
            result = self.call.callback(self.api, result)
        return result


def get_declared_api_functions(attrs):
    """Create a list of Application views instances from the passed
in 'attrs', plus any similar fields on the base classes (in 'bases')."""
    api_functions = {}
    for name, obj in list(attrs.items()):
        if isinstance(obj, api_function):
            #obj = attrs.pop(name)
            obj.name = name
            api_functions[name] = obj
    return api_functions


def hook(existing, callback):
    if existing:
        if not isinstance(existing, list):
            existing = [existing]
        existing.append(callback)
        return existing
    else:
        return callback


APIS = {}


class APItype(type):

    def __new__(cls, name, bases, attrs):
        abstract = attrs.pop('abstract', False)
        attrs['api_functions'] = get_declared_api_functions(attrs)
        if abstract:
            attrs['api_functions'] = []
        new_class = super(APItype, cls).__new__(cls, name, bases, attrs)
        if not abstract:
            name = new_class.__name__.lower()
            new_class.name = name
            APIS[name] = new_class
        return new_class


class API(APItype('API', (object,), {'abstract': True})):
    BASE_URL = None
    '''The base url used to construct the full url of api functions'''
    params = []
    auth_class = None
    abstract = True
    METHOD = 'GET'
    auth = None
    json = False

    @classmethod
    def build(cls, cfg=None):
        pass

    def __init__(self, http=None, **kwargs):
        if http is None:
            http = HttpClient()
        self.http = http
        if self.json:
            self.http.headers['content-type'] = 'application/json'
            self.http.headers['accept'] = 'application/json'
        self.setup(**kwargs)

    def build_auth(self, **kwargs):
        return self.auth_class(**kwargs)

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def __repr__(self):
        return self.name
    __str__ = __repr__

    def setup(self, **kwargs):
        pass

    def html_login_link(self, request):
        '''Build an HTML anchor for authenticating a user via this service.
        '''
        pass

    def request(self, call, url, data=None, pre_request=None,
                post_request=None, chain_to_response=None, **params):
        '''Send the request to the API provider.

        This method should not be invoked directly.

        :param call: The :class:`api_function` function invoking this method
        :param url: the absolute url of the API provider function.
        :param data: data to be sent as query in the url or in the body.
        '''
        method = call.method or self.METHOD
        pre_request = hook(pre_request,
                           lambda response: self.pre_request(call, response))
        post_request = hook(post_request,
                            lambda response: self.post_request(call, response))
        response = self.http.request(method,
                                     url,
                                     data=data,
                                     pre_request=pre_request,
                                     post_request=post_request,
                                     **params)
        if chain_to_response:
            response.chain_event(chain_to_response, 'post_request')
        return response

    def build_uri(self, base, *bits):
        if bits:
            path = '/'.join(bits)
            if not base.endswith('/'):
                base += '/'
            return base + path
        return base

    def pre_request(self, call, response):
        '''Called back before ``response`` is sent.
        '''
        return response

    def post_request(self, call, response):
        '''Called back after a full ``response`` is received.
        '''
        return response

    def handle_response(self, call, response):
        '''handle the ``response`` from a :class:`api_function` ``call``.
        '''
        response.raise_for_status()
        return response.decode_content()

    def authorized(self):
        return False

    def user_data(self):
        raise NotImplementedError()
