from pulsar import get_actor
from pulsar.apps import rpc, ws

from .models import PulsarServer


__all__ = ['rpc_proxy_middleware',
           'LazyRpcProxy']


class LazyRpcProxy(object):
    '''Lazy class for handling RPC proxies'''
    def __init__(self, url, environ, **kwargs):
        self._url = url
        self._environ = environ
        self._proxy = None
        self.kwargs = kwargs

    def get_url(self, user, code=None):
        '''Obtain the rpc url for *user*.'''
        code = code or self._url
        if isinstance(code, PulsarServer):
            return code.path
        else:
            rpc = PulsarServer.objects.filter(code=code)
            if rpc.count():
                return rpc[0].path
            else:
                return code

    def proxy(self):
        if self._proxy is None:
            self._proxy = self._setup()
        return self._proxy

    def __getattr__(self, name):
        return getattr(self.proxy(), name)

    def get_rpc_handler(self, path):
        conn = self._environ.get('pulsar.connection')
        if conn:
            hnd = conn.actor.app_handler.get(path)
            if not hnd:
                raise ValueError('Could not fine RPC server %s.' % path)
            return hnd
        else:
            raise djpcms.ImproperlyConfigured('You cannot use the\
 rpc_middleware if not using pulsar as server')

    def _setup(self):
        user = self._environ.get('user')
        path = self.get_url(user, self._url)
        client_version = self.kwargs.pop('client_version',
                                         self._environ.get('HTTP_USER_AGENT'))
        if path.startswith('/'):
            hnd = self.get_rpc_handler(path)
            return rpc.LocalJsonProxy(hnd.route,
                                      handler=hnd.handler,
                                      environ=self._environ,
                                      client_version=client_version)
        else:
            return self.proxyhandler(path, user,
                                     client_version=client_version,
                                     **self.kwargs)

    def proxyhandler(self, path, user, **kwargs):
        return rpc.JsonProxy(path, **kwargs)


class rpc_proxy_middleware(object):
    '''A WSGI_ middleware which add aN rpc proxy to the environment dictionary.

:parameter domain: The domain of the rpc server. It can be an absolute url,
    such as ``http::/myrpcserver.com:8060`` or a name.

Add two entries to the environment:

* ``rpc_proxy`` the proxy handler for :attr:`domain`
* ``rpc_handler`` The constructor for a rpc proxies.
'''
    def __init__(self, domain=None, handlercls=None):
        self.domain = domain
        self.handlercls = handlercls or LazyRpcProxy

    def __call__(self, environ, start_response):
        environ['rpc_proxy'] = self.handlercls(self.domain, environ)
        environ['rpc_handler'] = self.handlercls
