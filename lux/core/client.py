from pulsar.api import Http401, PermissionDenied
from pulsar.utils.websocket import SUPPORTED_VERSIONS, websocket_key
from pulsar.apps.http.wsgi import HttpWsgiClient
from pulsar.apps.wsgi import wsgi_request
from pulsar.apps.greenio import GreenHttp

from lux.utils.token import encode_json
from lux.utils.url import initial_slash
from lux.utils.context import app_attribute, current_request

from .exceptions import raise_http_error


def app_token(request):
    app = request.app
    payload = {
        'app_name': app.config['APP_NAME'],
        'url': request.absolute_uri('/')[:-1]
    }
    app.fire('on_jwt', request, payload)
    return encode_json(
        payload,
        app.config['SECRET_KEY'],
        algorithm=app.config['JWT_ALGORITHM']
    )


def app_client(app, green=True):
    # make sure request handler is setup
    app.request_handler()
    http = AppClient(app)
    http.headers['user-agent'] = app.config['APP_NAME']
    return GreenHttp(http) if app.green_pool and green else http


class AppClient(HttpWsgiClient):
    """A client for interacting with a REST APIs
    """
    async def request(self, method, url, token=None, jwt=False, oauth=None,
                      headers=None, auth_error=None, **kw):
        wsgi_request = current_request()
        headers = list(headers or ())
        if wsgi_request:
            agent = wsgi_request.get('HTTP_USER_AGENT')
            if agent:
                headers.append(('user-agent', agent))

        if wsgi_request:
            if jwt:
                jwt = app_token(wsgi_request)
            else:
                if not token and wsgi_request.cache.get('session'):
                    token = wsgi_request.cache.session.token

        if token:
            headers.append(('Authorization', 'Bearer %s' % token))
        elif oauth:
            headers.append(('Authorization', 'OAuth %s' % oauth))
        elif jwt:
            headers.append(('Authorization', 'JWT %s' % jwt))

        url = 'http://local%s' % initial_slash(url)
        response = await super().request(
            method, url, headers=headers, **kw
        )
        try:
            raise_http_error(response, method, url)
        except (Http401, PermissionDenied) as exc:
            self.app.logger.error(str(exc))
            if auth_error:
                raise auth_error from None
            raise
        return response

    def wsget(self, path=None, headers=None, **kw):
        """make a websocket request"""
        if headers is None:
            headers = []
        headers.extend((
            ('Connection', 'Upgrade'),
            ('Upgrade', 'websocket'),
            ('Sec-WebSocket-Version', str(max(SUPPORTED_VERSIONS))),
            ('Sec-WebSocket-Key', websocket_key())
        ))
        return self.request('GET', path=path, headers=headers, **kw)

    def run_command(self, command, argv=None, **kwargs):
        """Run a lux command"""
        argv = argv or []
        cmd = self.wsgi_callable.get_command(command)
        return cmd(argv, **kwargs)

    def wsgi_request(self, response):
        return wsgi_request(response.server_side.request.environ)


@app_attribute
def http_local(app):
    return GreenHttp(HttpWsgiClient(app))
