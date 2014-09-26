from ..oauth import OAuth2, register_oauth


@register_oauth
class Linkedin(OAuth2):
    '''LinkedIn api

    https://developer.linkedin.com/apis
    '''
    auth_uri = 'https://www.linkedin.com/uas/oauth2/authorization'
    token_uri = 'https://www.linkedin.com/uas/oauth2/accessToken'
