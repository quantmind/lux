'''
'''
from ..oauth import OAuth1


twitter_cards = {}


def twitter_card(cls):
    type = cls.__name__.lower()
    twitter_cards[type] = cls()
    return cls


class Twitter(OAuth1):
    auth_uri = 'https://api.twitter.com/oauth/authorize'
    request_token_uri = 'https://api.twitter.com/oauth/request_token'
    token_uri = 'https://api.twitter.com/oauth/access_token'
    fa = 'twitter-square'

    def on_html_document(self, request, doc):
        card = 'summary'
        if 'card' in self.config:
            card = self.config['card']
        doc.meta.set('twitter:card', card)

    def ogp_add_tags(self, request, ogp):
        '''Add meta tags to an HTML5 document
        '''
        doc = ogp.doc
        card = 'summary'
        site = self.config.get('site')
        if 'card' in self.config:
            card = self.config['card']
        twitter = doc.meta.namespaces.get('twitter')
        if twitter:
            card = twitter.get('card', card)
        if card and site:
            Card = twitter_cards.get(card)
            if Card:
                doc.head.add_meta(name='twitter:card', content=card)
                doc.head.add_meta(name='twitter:site', content=site)
                Card(doc)
            else:
                request.logger.warning(
                    'Twitter card not defined but card is available')


class TwitterCard:
    prefix = 'twitter'
    default_meta_key = 'name'

    def set(self, doc, key, array=False):
        twitter = doc.meta.namespaces.get(self.prefix)
        if twitter and key in twitter:
            value = twitter[key]
        else:
            # get the value for the og meta
            value = doc.head.get_meta('og:%s' % key, 'property')
        if value:
            doc.head.add_meta(name='twitter:%s' % key, content=value)


@twitter_card
class Summary(TwitterCard):

    def __call__(self, doc):
        self.set(doc, 'title')
        self.set(doc, 'description')
        self.set(doc, 'image')


@twitter_card
class Summary_Large_Image(Summary):
    pass


@twitter_card
class Photo(Summary):
    pass
