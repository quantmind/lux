from oauthlib import oauth2

from pulsar.apps.http import Auth

from .binder import API


__all__ = ['oauth2', 'OAuth2', 'OAuth2API']


class OAuth2(Auth):
    '''Construct a new OAuth 2 authorisation object.

        :param client_id: Client id obtained during registration
        :param client: :class:`oauthlib.oauth2.Client` to be used. Default is
                       WebApplicationClient which is useful for any
                       hosted application but not mobile or desktop.
        :param token: Token dictionary, must include access_token
                      and token_type.
    '''
    def __init__(self, client_id=None, client=None, **kwargs):
        self._client = client or oauth2.WebApplicationClient(client_id,
                                                             **kwargs)

    def __call__(self, response):
        request = response.request
        full_url = request.full_url
        url, headers, body = self._client.add_token(
            full_url,
            http_method=request.method,
            body=request.data,
            headers=request.headers)
        if url != full_url:
            request.full_url = url
        return response


class OAuth2API(API):
    WEB_AUTH_URL = None

    def setup(self, client_id=None, client_secret=None, client_scope=None,
              **params):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_scope = client_scope

    def web_oauth(self, request):
        '''Return the absolute uri for web authentication.

        Uses the :attr:`WEB_AUTH_URL` attribute as the base url.
        '''
        redirect_uri = self.build_uri(request.absolute_uri(), self.name,
                                      'callback')
        sessions = request.app.extensions['sessions']
        client = oauth2.WebApplicationClient(self.client_id)
        state = sessions.get_or_create_csrf_token(request)
        return client.prepare_request_uri(self.WEB_AUTH_URL,
                                          scope=self.client_scope,
                                          redirect_uri=redirect_uri,
                                          state=state)
