from lux import Html, Parameter
from lux.extensions.services import OAuth2API, api_function, OAuth2, oauth2


class Amazon(OAuth2API):
    WEB_AUTH_URL = 'https://www.amazon.com/ap/oa'
    BASE_URL = 'https://api.amazon.com'
    scopes = ('user', 'user:email', 'user:follow', 'public_repo', 'repo',
              'repo:status', 'delete_repo', 'notifications', 'gist')
    auth_class = OAuth2
    json = True
    params = [Parameter('AMAZON_CLIENT_ID', None,
                        'Amazon OAUth client ID'),
              Parameter('AMAZON_CLIENT_SECRET', None,
                        'Amazon OAUth secret'),
              Parameter('AMAZON_SCOPE', 'profile',
                        'Amazon application scope')]

    @classmethod
    def build(cls, cfg=None):
        if cfg:
            id = cfg.get('AMAZON_CLIENT_ID')
            secret = cfg.get('AMAZON_CLIENT_SECRET')
            if id and secret:
                return cls(client_id=id,
                           client_secret=secret,
                           client_scope=cfg.get('AMAZON_SCOPE') or 'profile')

    def html_login_link(self, request):
        img = Html('img', src=('https://images-na.ssl-images-amazon.com/images'
                               '/G/01/lwa/btnLWA_gold_156x32.png'),
                   width=156, height=32, alt='Login with Amazon')
        href = self.web_oauth(request)
        return Html('a', img, href=href)

    authorization = api_function(
        '/auth/o2',
        method='GET',
        allowed_params={'state': None,
                        'response_type': 'code',   # token or code
                        'redirect_uri': None},
        required_params=('response_type',),
        allow_redirects=False)
