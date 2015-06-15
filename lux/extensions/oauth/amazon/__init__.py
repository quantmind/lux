from ..oauth import OAuth2, register_oauth


@register_oauth
class Amazon(OAuth2):
    auth_uri = 'https://www.dropbox.com/1/oauth2/authorize'
    token_uri = 'https://api.dropbox.com/1/oauth2/token'
