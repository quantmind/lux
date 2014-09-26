from ..oauth import OAuth2, register_oauth


@register_oauth
class Facebook(OAuth2):
    namespace = 'fb'
    auth_uri = 'https://www.facebook.com/dialog/oauth'
    token_uri = 'https://graph.facebook.com/oauth/access_token'
    default_scope = ['public_profile', 'email']

    def ogp_add_tags(self, request, ogp):
        '''Add meta tags to an HTML5 document
        '''
        key = self.config.get('key')
        if key:
            ogp.prefixes.append('fb: http://ogp.me/ns/fb#')
            ogp.doc.head.add_meta(property='fb:app_id', content=key)
