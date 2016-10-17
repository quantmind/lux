
ogp_types = {}


def ogp_type(cls):
    type = cls.__name__.lower()
    ogp_types[type] = cls()
    return cls


class OGP:

    def __init__(self, doc):
        self.doc = doc
        self.prefixes = []
        og = doc.meta.namespaces.get('og')
        if og:
            type = og.get('type')
            if type:
                self.add_type(type)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if not type and self.prefixes:
            prefix = ' '.join(self.prefixes)
            self.doc.attr('prefix', prefix)

    def add_type(self, type):
        prefix = 'og: http://ogp.me/ns#'
        if type is not 'website':
            bits = type.split('.')
            if not self.prefixes:
                self.prefixes.append(prefix)
            prefix = '{0}: http://ogp.me/ns/{0}#'.format(bits[0])
        if prefix not in self.prefixes:
            type_handler = ogp_types.get(type)
            if type_handler:
                self.doc.head.add_meta(property='og:type', content=type)
                self.prefixes.append(prefix)
                type_handler(self.doc)


class OGPType:

    def __call__(self, doc):
        pass

    def set(self, doc, key, tag_key=None, array=False):
        '''Set a key in the doc meta tags
        '''
        value = doc.meta.namespaces['og'].get(key)
        if not value and tag_key:
            value = doc.meta.get(tag_key)
            if value and array:
                value = value.split(', ')
        if value:
            key = 'og:%s' % key
            if not isinstance(value, (tuple, list)):
                value = (value,)
            if not array:
                value = value[:1]
            for v in value:
                doc.head.add_meta(property=key, content=v)


@ogp_type
class Website(OGPType):

    def __call__(self, doc):
        self.set(doc, 'url')
        self.set(doc, 'title', 'title')
        self.set(doc, 'description', 'description')
        self.set(doc, 'locale')
        self.set(doc, 'site_name')
        self.set(doc, 'image', array=True)


@ogp_type
class Profile(Website):

    def __call__(self, doc):
        super().__call__(doc)
        self.set(doc, 'first_name')
        self.set(doc, 'last_name')
        self.set(doc, 'username')
        self.set(doc, 'gender')


@ogp_type
class Article(Website):

    def __call__(self, doc):
        super().__call__(doc)
        self.set(doc, 'published_time')
        self.set(doc, 'modified_time')
        self.set(doc, 'expiration_time')
        self.set(doc, 'author', 'author', array=True)
        self.set(doc, 'section')
        self.set(doc, 'tag', 'keywords', array=True)
