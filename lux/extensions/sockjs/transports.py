from datetime import datetime

from pulsar import Http404
from pulsar.utils.httpurl import CacheControl

CACHE_TIME = 31536000
nocache = CacheControl(nostore=True)
cache = CacheControl(maxage=CACHE_TIME)
APPJSON = 'application/json'
PRELUDE = 'h' * 2048 + '\n'


class Transport(object):
    access_methods = 'OPTIONS, POST'

    __slots__ = ['handshake', 'handle']

    def __init__(self, request, handle=None):
        self.handshake = request
        self.handle = handle

    @property
    def response(self):
        return self.request.response

    @property
    def protocol(self):
        return self.request.connection._current_consumer

    def write(self, msg):
        raise NotImplementedError

    def session(self):
        server = self.request.urlargs['server']
        session = self.request.urlargs['session']
        self.request.cache.sockjs_session = session
        try:
            if len(server) != 3:
                raise ValueError
            int(server)
        except Exception:
            raise Http404
        return session

    def options(self):
        self.enable_cache()
        self.cors()
        response = self.response
        if self.verify_origin():
            response['Access-Control-Allow-Methods'] = self.allowed_methods
            response['Allow'] = self.allowed_methods
            response.status_code = 204
        else:
            response.status_code = 403
        return response

    def cors(self):
        '''Handle Cross domain communication
        '''
        request = self.request
        origin = request.get('HTTP_ORIGIN', '*')
        headers = request.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
        response = request.response

    def verify_origin(self):
        """Verify if request can be served"""
        # TODO: Verify origin
        return True

        # Respond with '*' to 'null' origin
        if origin == 'null':
            origin = '*'

        response['Access-Control-Allow-Origin'] = origin
        if headers:
            response['Access-Control-Allow-Headers'] = headers
        response['Access-Control-Allow-Credentials'] = 'true'

    def enable_cache(self):
        response = self.response
        cache(response.headers)
        d = datetime.now() + timedelta(seconds=CACHE_TIME)
        response['Expires'] = d.strftime('%a, %d %b %Y %H:%M:%S')
        response['access-control-max-age'] = CACHE_TIME


class Xhr(Transport):

    def start(self):
        nocache(self.response)
        self.cors()
        self.handl.on_start(self)


class XhrStreaming(Transport):

    def start(self):
        request.content_type = APPJSON
        self.session()
        nocache(self.request.response)
        self.cors()
        self.write(PRELUDE)
        self.handl.on_start(self)

    def write(self, msg):
        c = self.protocol
        c.write(msg)
