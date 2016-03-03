from ..oauth import OAuth2, OAuth2Api


class Api(OAuth2Api):
    url = 'https://api.github.com'
    headers = [('content-type', 'application/json')]

    def user(self):
        url = '%s/user' % self.url
        response = self.http.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()


class Github(OAuth2):
    '''Github api

    https://developer.github.com/v3/
    '''
    auth_uri = 'https://github.com/login/oauth/authorize'
    token_uri = 'https://github.com/login/oauth/access_token'
    fa = 'github-square'
    username_field = 'login'

    api = Api
