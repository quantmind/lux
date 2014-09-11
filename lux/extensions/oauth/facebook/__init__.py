from ..oauth import OAuth2, OGP, register_oauth


@register_oauth
class Facebook(OAuth2):
    namespace = 'fb'
    auth_uri = 'https://www.facebook.com/dialog/oauth'
    token_uri = 'https://graph.facebook.com/oauth/access_token'
    default_scope = ['public_profile', 'email']

    def add_meta_tags(self, request, doc):
        '''Add meta tags to an HTML5 document
        '''
        o = OGP(request, doc)
        key = self.config.get('key')
        if key:
            o.add_meta(doc, 'app_id', key, prefix='fb')
