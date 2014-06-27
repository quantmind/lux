'''OAuth account handling

Google and Twitter for now
'''
import json

from ..sessions import OAuth1, OAuth2, register_oauth
from .models import User, Oauth


def add_oauth(user, name, identifier, image=None, url=None, data=None):
    oauths = user.oauths
    oauth = None
    for index, o in enumerate(user.oauths):
        if o.name == name:
            if o.identifier != identifier:
                user.oauths.pop(index)
            else:
                oauth = o
                break
    if not oauth:
        oauth = Oauth(name=name, identifier=identifier, image=image,
                      url=url, data=data)
    else:
        oauth.image = image
        oauth.url = url
        oauth.data = data
    user.oauths.append(oauth)
    user.put()


class Google(OAuth2):
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://accounts.google.com/o/oauth2/token"

    def create_user(self, token, user=None):
        oauth = self.oauth(token=token)
        r = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
        if r.status_code == 200:
            data = json.loads(r.content)
            email = data['email']
            current = user if user and user.is_authenticated() else None
            user = User.get_by_email(email)
            if not user:
                # Find using oauths
                user = User.get_by_oauth('google', email)
            #
            if user and current:
                if user != current:
                    raise OauthError(
                        'Looks like another user is registered with %s' %
                        email)
                user = current
            if not user:
                if not current:
                    username = User.unique_username(data['name'])
                    user = User(username=username,
                                email=email,
                                active=True,
                                name=data['given_name'],
                                surname=data['family_name'])
                else:
                    user = current
            data['token'] = token
            add_oauth(user, 'google', email, image=data.get('picture'),
                      data=data)
            return user


class Twitter(OAuth1):
    auth_uri = 'https://api.twitter.com/oauth/authorize'
    request_token_uri = 'https://api.twitter.com/oauth/request_token'
    token_uri = 'https://api.twitter.com/oauth/access_token'

    def create_user(self, token, user=None):
        oauth = self.oauth(resource_owner_key=token['oauth_token'],
                           resource_owner_secret=token['oauth_token_secret'])
        r = oauth.get('https://api.twitter.com/1.1/account/settings.json')
        if r.status_code == 200:
            name = 'twitter'
            data = json.loads(r.content)
            base = data.pop('screen_name')
            current = user if user and user.is_authenticated() else None
            user = User.get_by_oauth(name, base)
            #
            if user and current:
                if user != current:
                    raise OauthError(
                        'Looks like another user is registered with %s' %
                        base)
                user = current
            #
            if not user:
                if not current:
                    username = User.unique_username(base)
                    user = User(username=username,
                                active=False)
                else:
                    user = current
            data['token'] = token
            add_oauth(user, name, base, image=data.get('picture'),
                      data=data)
            return user


register_oauth('twitter', Twitter)

register_oauth('google', Google)
