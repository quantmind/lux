import sys
from random import randint

from pulsar import HttpException, Http404
from pulsar.utils.system import json
from pulsar.utils.pep import ispy3k
from pulsar.apps.ws import WebSocket

from lux import Router, RouterParam, route, headers

from .transports import Xhr, XhrStreaming, APPJSON, nocache


if ispy3k:
    MAXSIZE = sys.maxsize
else:
    MAXSIZE = int((1 << 31) - 1)



class SockJs(Router):

    response_content_types = RouterParam(['text/plain', APPJSON])
    websockets_enabled = RouterParam(True)
    cookie_needed = RouterParam(False)

    def __init__(self, route, handle, **kwargs):
        super(SockJs, self).__init__(route, **kwargs)
        self.handle = handle
        if self.websockets_enabled:
            self.add_child(WebSocket('/websocket', handle))
        self.add_child(SockTransports('/<server>/<session>/', handle))

    @headers('text/plain', cache=nocache)
    def get(self, request):
        response = request.response
        response.content = 'Welcome to SockJS!\n'
        response._can_store_cookies = False
        return response

    @route('/')
    @headers('text/plain', cache=nocache)
    def get_base(self, request):
        response = request.response
        response.content = 'Welcome to SockJS!\n'
        response._can_store_cookies = False
        return response

    @route('/iframe<key>.html')
    def iframe(self, request):
        pass

    @route('/info')
    def info_get(self, request):
        response = request.response
        response.content_type = APPJSON
        data = {'websocket': self.websockets_enabled,
                'entropy': randint(0, MAXSIZE),
                'cookie_needed': self.cookie_needed,
                'origins': ['*:*']}
        response.content = json.dumps(data)
        nocache(response)
        cors(request)
        response._can_store_cookies = False
        return response

    @route('/info', method='options')
    def info_options(self, request):
        return Transport(request).options()


class SockTransports(Router):

    def __init__(self, route, handle, **kwargs):
        super(SockTransports, self).__init__(route, **kwargs)
        self.handle = handle

    def session(self, request):
        server = request.urlargs['server']
        session = request.urlargs['session']
        request.cache.sockjs_session = session
        try:
            if len(server) != 3:
                raise ValueError
            int(server)
        except Exception:
            raise Http404
        return session

    def get(self, request):
        raise Http404

    @route('xhr_streaming', method='post')
    def xhr_streaming(self, request):
        websocket = XhrStreaming(request)
        websocket.start()

    @route('xhr', method='post')
    def xhr(self, request):
        websocket = Xhr(request)
        websocket.start()

    @route('xhr_send', method='post')
    def xhr_send(self, request):
        data = yield request.body_data()
        msg = json.loads(data)
        self.handle.on_message(WebSocketProxy(request), msg)
        request.response.status_code = 204
        return request.response
