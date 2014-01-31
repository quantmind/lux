from lux.extensions.services import API, api_function, OAuth2


class OAuth:
    '''Google OAuth 2.0

https://developers.google.com/accounts/docs/OAuth2

To register a new client application go to

https://code.google.com/apis/console
'''
    AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/auth'
    ACCESS_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetAccessToken'
    DEFAULT_SCOPE = 'https://www.googleapis.com/auth/userinfo.profile'

    def extra_request_parameters(self):
        scopes = request.settings.GOOGLE_SCOPES
        scopes_string = ' '.join((str(scope) for scope in scopes))
        return {'scope': scopes_string}

    def authenticated_api(self, key, secret):
        auth = GoogleApi(*self.tokens)
        api = GoogleApi(auth)
        api.set_access_token(key, secret)
        return api

    def client(self, key=None, secret=None, **kwargs):
        tks = {}
        ot = OAuthToken(key, secret, self.scopes)
        for scope in self.scopes:
            tks[scope] = ot
        store = TokenStore(tks)
        pass


class Google(API):
    oauth_class = OAuth2

    def has_registration(self, cfg=None):
        if cfg:
            self.oauth.consumer.id = cfg.get('GOOGLE_CLIENT_ID')
            self.oauth.consumer.secret = cfg.get('GOOGLE_CLIENT_SECRET')
            return self.oauth.consumer.is_valid()
