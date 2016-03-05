from pulsar.utils.slugify import slugify

from ..oauth import OAuth2, OAuth2Api

fields = ('firstName,lastName,email-address,formatted-name,'
          'headline,location,industry')


class Api(OAuth2Api):
    url = 'https://api.linkedin.com/v1/people'
    headers = [('content-type', 'application/json'),
               ('x-li-format', 'json')]
    format = {'format': 'json'}
    username_field = 'username'
    email_field = 'email'
    firstname_field = 'firstName'
    lastname_field = 'lastName'

    def user(self):
        url = '%s/~:(%s)' % (self.url, fields)
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

    def username(self, user_data):
        return slugify('%s.%s' % (user_data['firstName'],
                                  user_data['lastName']))

    def firstname(self, user_data):
        return user_data['firstName']

    def lastname(self, user_data):
        return user_data['lastName']

    def email(self, user_data):
        return user_data['emailAddress']
