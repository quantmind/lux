import os
from functools import partial, total_ordering

from pulsar.utils.slugify import slugify


identity = lambda x, cfg: x

SEP = ', '
as_list = lambda x, cfg, w=identity: [w(v.strip(), cfg) for v in x.split(',')]

def list_of(W):
    return lambda x, cfg: as_list(x, cfg, W)


def meta_iterator(meta, params=None):
    if meta:
        for n, m in meta.items():
            if isinstance(m, Single):
                p = params.pop(n, None) if params else None
                m = m[0] if m else p
            yield slugify(n, separator='_'), m
    if params:
        for n, m in params.items():
            yield n, m


class Processor:

    def __init__(self, name, processor=None, default=None, multiple=False,
                 docs=None):
        self.name = slugify(name, separator='_')
        self._default = default
        self.process = processor or as_list
        self.multiple = multiple
        self.docs = docs

    def __call__(self, cfg):
        meta = Multi() if self.multiple else Single()
        default = self._default
        if hasattr(self._default, '__call__'):
            default = default(cfg)
        meta.extend(default)
        return meta


class Multi(list):

    def extend(self, values):
        if values:
            if isinstance(values, str) or not hasattr(values, '__iter__'):
                values = (values,)
            super(Multi, self).extend(values)

    def value(self):
        return self

    def join(self, sep=SEP):
        return sep.join(('%s' % v for v in self))

    def __str__(self):
        return self.join()


class Single(Multi):

    def value(self):
        return self.join() if self else None


def guess(value):
    return Multi(value) if len(value) > 1 else Single(value)


#@total_ordering
class URLWrapper:

    def __init__(self, name, settings):
        # next 2 lines are redundant with the setter of the name property
        # but are here for clarity
        self.settings = settings
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.slug = slugify(name)

    def as_dict(self):
        d = self.__dict__
        d['name'] = self.name
        return d

    def __hash__(self):
        return hash(self.slug)

    def _key(self):
        return self.slug

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{} {}>'.format(type(self).__name__, str(self))


class Category(URLWrapper):
    pass


class Tag(URLWrapper):
    pass


class Author(URLWrapper):
    pass
