from ..oauth import OAuth2, OAuth2Api


class Api(OAuth2Api):
    url = 'https://api.linkedin.com/v1/people'
    headers = [('content-type', 'application/json'),
               ('x-li-format', 'json')]
    format = {'format': 'json'}

    def user(self):
        url = '%s/~' % self.url
        response = self.http.get(url, data=self.format, headers=self.headers)
        response.raise_for_status()
        return response.json()


class Linkedin(OAuth2):
    '''LinkedIn api

    https://developer.linkedin.com/apis
    '''
    auth_uri = 'https://www.linkedin.com/uas/oauth2/authorization'
    token_uri = 'https://www.linkedin.com/uas/oauth2/accessToken'
    fa = 'linkedin-square'
    api = Api
