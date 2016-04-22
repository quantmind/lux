import sys
import hashlib
from random import randint

from pulsar import HttpException
from pulsar.apps.wsgi import Router, Json, route
from pulsar.utils.httpurl import CacheControl

from .transports.websocket import WebSocket
from .utils import IFRAME_TEXT


class SocketIO(Router):
    """A Router for sockjs requests
    """
    info_cache = CacheControl(nostore=True)
    home_cache = CacheControl(maxage=60*60*24*30)

    def __init__(self, route, handle, **kwargs):
        super().__init__(route, **kwargs)
        self.handle = handle
        self.add_child(WebSocket('/websocket', self.handle, **kwargs))
        self.add_child(WebSocket('<server_id>/<session_id>/websocket',
                                 self.handle, **kwargs))

    def get(self, request):
        response = request.response
        self.home_cache(response.headers)
        response.content_type = 'text/plain'
        response.content = 'Welcome to SockJS!\n'
        return response

    @route(method=('options', 'get'))
    def info(self, request):
        response = request.response
        self.info_cache(response.headers)
        self.origin(request)
        return Json({'websocket': request.config['WEBSOCKET_AVAILABLE'],
                     'origins': ['*:*'],
                     'entropy': randint(0, sys.maxsize)}
                    ).http_response(request)

    @route('iframe[0-9-.a-z_]*.html', re=True,
           response_content_types=('text/html',))
    def iframe(self, request):
        response = request.response
        url = request.absolute_uri(self.full_route.path)
        response.content = IFRAME_TEXT % url
        hsh = hashlib.md5(response.content[0]).hexdigest()
        value = request.get('HTTP_IF_NONE_MATCH')

        if value and value.find(hsh) != -1:
            raise HttpException(status=304)

        self.home_cache(response.headers)
        response['Etag'] = hsh
        return response

    def origin(self, request):
        """Handles request authentication
        """
        response = request.response
        origin = request.get('HTTP_ORIGIN', '*')

        # Respond with '*' to 'null' origin
        if origin == 'null':
            origin = '*'

        response['Access-Control-Allow-Origin'] = origin

        headers = request.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
        if headers:
            response['Access-Control-Allow-Headers'] = headers

        response['Access-Control-Allow-Credentials'] = 'true'
