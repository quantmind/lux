from ..oauth import OAuth2, register_oauth


@register_oauth
class Github(OAuth2):
    '''Github api

    https://developer.github.com/v3/
    '''
    auth_uri = 'https://github.com/login/oauth/authorize'
    token_uri = 'https://github.com/login/oauth/access_token'
