'''OAuth account handling

Google and Twitter for now
'''
import json

from ..sessions import OAuth1, OAuth2, register_oauth
from .models import User


class Google(OAuth2):
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://accounts.google.com/o/oauth2/token"

    def create_user(self, token):
        oauth = self.oauth(token=token)
        r = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
        if r.status_code == 200:
            data = json.loads(r.content)
            email = data['email']
            user = User.get_by_email(email)
            if user:
                user.google_token = token
            else:
                username = User.unique_username(data['name'])
                user = User(username=username,
                            email=email,
                            name=data['given_name'],
                            surname=data['family_name'],
                            google_id=data['id'],
                            google_token=token)
            user.put()
            return user


class Twitter(OAuth1):
    auth_uri = 'https://api.twitter.com/oauth/authorize'
    request_token_uri = 'https://api.twitter.com/oauth/request_token'
    token_uri = 'https://api.twitter.com/oauth/access_token'

    def create_user(self, token):
        oauth = self.oauth(resource_owner_key=token['oauth_token'],
                           resource_owner_secret=token['oauth_token_secret'])
        r = oauth.get('https://api.twitter.com/1.1/account/settings.json')
        if r.status_code == 200:
            data = json.loads(r.content)
            base = data.pop('screen_name')
            q = User.query(User.twitter_name == base)
            if q.count():
                return q[0]
            else:
                username = base
                count = 0
                while True:
                    q = User.query(User.username == username)
                    if not q.count():
                        break
                    count += 1
                    username = '%s%s' % (base, count)
                user = User(username=username,
                            twitter_name=base,
                            twitter_token=token)
                user.put()
                return user


register_oauth('twitter', Twitter)

register_oauth('google', Google)
