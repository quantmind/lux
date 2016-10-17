from pulsar.utils.slugify import slugify


SEP = ', '


def identity(x, cfg):
    return x


class Processor:

    def __init__(self, name, processor=None):
        self.name = slugify(name, separator='_')
        self._processor = processor

    def __call__(self, values=None, cfg=None):
        if values:
            if self._processor:
                return self._processor(values[-1], cfg)
            else:
                return values[-1]


class MultiValue(Processor):

    def __init__(self, name=None, cls=None):
        self.name = slugify(name, separator='_') if name else ''
        self.cls = cls or identity

    def __call__(self, values=None, cfg=None):
        all = []
        if values:
            for x in values:
                all.extend((self.cls(v.strip(), cfg) for v in x.split(',')))
        return all


class URLWrapper:

    def __init__(self, name, settings):
        self.settings = settings
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.slug = slugify(name)

    def __call__(self, app):
        # TODO
        return self.name

    def __hash__(self):
        return hash(self.slug)

    def _key(self):
        return self.slug

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self)


class Category(URLWrapper):
    pass


class Tag(URLWrapper):
    pass


class Author(URLWrapper):
    pass
