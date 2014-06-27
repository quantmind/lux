'''OAuth account handling
'''

__all__ = ['OAuth1', 'OAuth2', 'register_oauth']


class OAuth1(object):
    '''OAuth version 1
    '''
    version = 1
    auth_uri = None
    token_uri = None

    def __init__(self, config):
        self.config = config

    def authorization_url(self, request, redirect_uri):
        oauth = self.oauth()
        token = oauth.fetch_request_token(self.request_token_uri)
        owner_key = token.get('oauth_token')
        owner_secret = token.get('oauth_token_secret')
        cache = request.cache_server
        cache.add(key=owner_key, value=owner_secret, time=600)
        return oauth.authorization_url(self.auth_uri)

    def access_token(self, request, data, redirect_uri=None):
        oauth_token = data['oauth_token']
        cache = request.cache_server
        oauth_secret = cache.get(oauth_token)
        verifier = data['oauth_verifier']
        oauth = self.oauth(resource_owner_key=oauth_token,
                           resource_owner_secret=oauth_secret,
                           verifier=verifier)
        return oauth.fetch_access_token(self.token_uri)

    def oauth(self, **kw):
        from requests_oauthlib import OAuth1Session
        p = self.config
        return OAuth1Session(p['key'], client_secret=p['secret'], **kw)

    def create_user(self, token, user=None):
        raise NotImplementedError


class OAuth2(OAuth1):
    '''OAuth version 2
    '''
    version = 2

    def authorization_url(self, request, redirect_uri):
        oauth = self.oauth(redirect_uri=redirect_uri)
        return oauth.authorization_url(self.auth_uri)[0]

    def access_token(self, request, data, redirect_uri=None):
        oauth = self.oauth(redirect_uri=redirect_uri)
        return oauth.fetch_token(self.token_uri,
                                 client_secret=self.config['secret'],
                                 code=data.get('code'))

    def oauth(self, **kw):
        from requests_oauthlib import OAuth2Session
        p = self.config
        return OAuth2Session(p['key'], scope=p['scope'], **kw)


def register_oauth(name, cls):
    global Accounts
    Accounts[name] = cls


Accounts = {}
