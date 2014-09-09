from ..oauth import OAuth2, OGP, register_oauth


@register_oauth
class Facebook(OAuth2):
    auth_uri = 'https://www.facebook.com/dialog/oauth'
    token_uri = 'https://graph.facebook.com/oauth/access_token'
    default_scope = ['public_profile', 'email']

    def add_meta_tags(self, request, doc):
        '''Add meta tags to an HTML5 document
        '''
        OGP(request, doc)
        key = self.config.get('key')
        prefix = doc.attr('prefix')
        if key and prefix:
            doc.attr('prefix', '%s fb: http://ogp.me/ns/fb#' % prefix)
            doc.head.add_meta(property='fb:app_id', content=key)
