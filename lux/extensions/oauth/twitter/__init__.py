'''
'''
from ..oauth import OAuth1, OGP, register_oauth


@register_oauth
class Twitter(OAuth1):
    auth_uri = 'https://api.twitter.com/oauth/authorize'
    request_token_uri = 'https://api.twitter.com/oauth/request_token'
    token_uri = 'https://api.twitter.com/oauth/access_token'

    def add_meta_tags(self, request, doc):
        '''Add meta tags to an HTML5 document
        '''
        site = self.config.get('site')
        if not site:
            request.logger.warning(
                'Twitter site not defined. Cannot add twitter card')
            return
        t = TwitterCard(request, doc, self.config.get('card'))
        t.add_meta(doc, 'site', site)


class TwitterCard(OGP):
    prefix = 'twitter'
    default_type = 'summary'
    field_mapping = {'type': 'card'}
    card_types = {
        'summary': (),
        'summary_large_image': (),
        'photo': ()
    }
