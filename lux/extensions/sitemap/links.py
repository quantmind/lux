from pulsar.apps.wsgi import HtmlVisitor, AsyncString

from lux import Template


__all__ = ['ImageProvider', 'Link']


Link = Template(tag='a')


class A(HtmlVisitor):

    def add_data(self, html, key, value):
        if key == 'icon':
            icon = Icon(html.tag, value)
            html.prepend(icon)
        elif key == 'ajax' and value:
            html.addClass('ajax')
        else:
            super(A, self).add_data(html, key, value)


class Icon(AsyncString):
    '''Must set the ICON_PROVIDER parameter'''
    def __init__(self, tag, value, provider=None):
        super(Icon, self).__init__(value)
        self.tag = tag
        self.provider = provider

    def do_stream(self, request):
        if request and self.children:
            p = self.provider or request.app.config.get('ICON_PROVIDER')
            provider = IMAGE_PROVIDERS.get(p)
            if provider:
                yield provider(request, self.tag, self.children[0])


IMAGE_PROVIDERS = {}


class ImageType(type):

    def __new__(cls, name, bases, attrs):
        new_class = super(ImageType, cls).__new__(cls, name, bases, attrs)
        name = getattr(new_class, 'name', None)
        if name:
            IMAGE_PROVIDERS[name] = new_class()
        return new_class


class ImageProvider(ImageType('ImageBase', (object,), {})):

    def __call__(self, request, tag, image):
        raise NotImplemented


class FontAwesome(ImageProvider):
    name = 'fontawesome'

    def __call__(self, request, tag, image):
        return '<i class="icon-%s"></i>' % image
