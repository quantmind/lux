from ..oauth import OAuth2, OGP, register_oauth


@register_oauth
class Facebook(OAuth2):
    auth_uri = 'https://www.facebook.com/dialog/oauth'

    def add_meta_tags(self, request, doc):
        '''Add meta tags to an HTML5 document
        '''
        OGP(request, doc)
        prefix = doc.attr('prefix')
        if prefix:
            doc.attr('prefix', '%s fb: http://ogp.me/ns/fb#')
            doc.head.add_meta(name='fb:app_id', content=self.key)
