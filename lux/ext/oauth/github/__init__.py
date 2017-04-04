from ..oauth import OAuth2, OAuth2Api


class Api(OAuth2Api):
    url = 'https://api.github.com'

    def user(self):
        response = self.http.get('%s/user' % self.url)
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

    def username(self, user_data):
        return user_data.get('login')

    def firstname(self, user_data):
        return user_data.get('name')

    def lastname(self, user_data):
        return user_data.get('lastName')
