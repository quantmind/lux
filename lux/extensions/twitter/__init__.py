'''
'''
import lux
from lux import Parameter

card_types = {
    'summary': ('title', 'description', 'image', 'site', 'url'),
    'summary_large_image': ('title', 'description', 'image', 'site', 'url'),
    'photo': ('title', 'description')
}

card_mapping = {
    'description': ('summary',)
}


def twitter_card(request, **kwargs):
    app = request.app
    if app.config.get('TWITTER_CARD'):
        head = request.html_document.head
        type = card_content(request, 'type', kwargs)
        if not type:
            return
        info = card_types.get(type)
        if not info:
            app.logger.warning('Twitter card %s not available', type)
        else:
            head.add_meta(name='twitter:card', content=type)
            for entry in info:
                content = card_content(request, entry, kwargs)
                if content:
                    head.add_meta(name='twitter:%s' % entry, content=content)
                elif entry in card_mapping:
                    for name in card_mapping[entry]:
                        content = kwargs.get(name)
                        if content:
                            head.add_meta(name='twitter:%s' % entry,
                                          content=content)
                            break


def card_content(request, name, kwargs):
    tname = 'twitter-%s' % name
    if tname in kwargs:
        return kwargs[tname]
    elif name in kwargs:
        return kwargs.get(name)
    elif name == 'type':
        return 'summary'
    elif name == 'title':
        return request.html_document.head.title
    elif name == 'description':
        return request.html_document.head.get_meta('description')
    elif name == 'site':
        return request.app.config['TWITTER_SITE']
    elif name == 'url':
        return request.absolute_uri()


class Extension(lux.Extension):

    _config = [
        Parameter('TWITTER_CARD', True, 'Add twitter card'),
        Parameter('TWITTER_SITE', None,
                  'Default twitter site entry in a twitter card')]

    def on_html_document(self, app, request, doc):
        pass
