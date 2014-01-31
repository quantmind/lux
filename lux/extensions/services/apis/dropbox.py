from pulsar import PermissionDenied
from pulsar.utils.security import random_string
from pulsar.utils.httpurl import urlparse, parse_qs

from lux import Html, Parameter
from lux.extensions.services import API, api_function, OAuth2, oauth2


def authorize(api, response):
    '''Callback for *authorization* function.'''
    token = response['token']
    client = api.get_oauth(token)
    api.http.bind_event('pre_request', OAuth2(client=client))
    return response


class Dropbox(API):
    '''Github API v3 implementation.

    Documented in http://developer.github.com/
    To access the API you need the GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET
    parameters in the configuration.
    '''
    BASE_URL = 'https://api.dropbox.com/1'
    scopes = ('user', 'public_repo', 'repo', 'gist')
    auth_class = OAuth2
    json = True
    params = [Parameter('DROPBOX_CLIENT_ID', None,
                        'Dropbox OAuth client ID'),
              Parameter('DROPBOX_CLIENT_SECRET', None,
                        'Dropbox OAuth secret')]

    def setup(self, client_id=None, client_secret=None, **params):
        self.client_id = client_id
        self.client_secret = client_secret

    @classmethod
    def build(cls, cfg=None):
        if cfg:
            id = cfg.get('DROPBOX_CLIENT_ID')
            secret = cfg.get('DROPBOX_CLIENT_SECRET')
            if id and secret:
                return cls(client_id=id, client_secret=secret)

    authorization = api_function(
        'https://www.dropbox.com/1/oauth2/authorize',
        method='GET',
        allowed_params={'state': None,
                        'response_type': 'code',   # token or code
                        'client_id': None,
                        'redirect_uri': None},
        required_params=('response_type',),
        callback=authorize,
        allow_redirects=False)
    #
    token = api_function('oauth2/token',
                         method='POST',
                         allowed_params={'code': None,
                                         'client_id': None,
                                         'client_secret': None,
                                         'grant_type': 'authorization_code'},
                         required_params=('code', 'grant_type',))

    def pre_request(self, call, response):
        if call.name == 'authorization':
            request = response.request
            if 'client_id' not in request.query:
                #if not request.data.get('state'):
                #    request.data['state'] = random_string()
                request.data['client_id'] = self.client_id
        elif call.name == 'token':
            request = response.request
            request.data['client_id'] = self.client_id
            request.data['client_secret'] = self.client_secret
        return response

    def post_request(self, call, response):
        if response.status_code == 302 and call.name == 'authorization':
            url = urlparse(response.headers['location'])
            query = parse_qs(url.query)
            cont = query.get('cont')
            if cont:
                return self.request(call, cont[0], chain_to_response=response)
            else:
                state = query.get('state')
                #if state != response.request.data['state']:
                #    raise PermissionDenied('state mismatch')
                code = url.query['code'][0]
                return self.token(code=code, chain_to_response=response)
        return response
