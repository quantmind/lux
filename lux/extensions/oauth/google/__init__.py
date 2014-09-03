from ..oauth import OAuth2


@register_oauth
class Google(OAuth2):
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://accounts.google.com/o/oauth2/token"
