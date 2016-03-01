from ..oauth import OAuth2


class Dropbox(OAuth2):
    auth_uri = 'https://www.dropbox.com/1/oauth2/authorize'
    token_uri = 'https://api.dropbox.com/1/oauth2/token'
