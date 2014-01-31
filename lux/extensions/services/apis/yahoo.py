from lux.extensions.services import OAuth2API, api_function


class Yahoo(OAuth2API):
    WEB_AUTH_URL = 'https://github.com/login/oauth/authorize'
    BASE_URL = 'https://api.login.yahoo.com/oauth/v2'

    def user_data(self, access_token):
        api = YahooApi(self, access_token)
        guid = api.user_id()
        data = api.user_data(guid)
        return data, access_token.key, access_token.secret

    def authenticated_api(self, key, secret):
        token = self.OAuthToken(key, secret)
        return YahooApi(self, token)

    def get_user_details(self, response):
        return {'uid': response['guid']}
