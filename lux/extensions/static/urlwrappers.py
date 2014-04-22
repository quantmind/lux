import os
from functools import partial, total_ordering

from pulsar.utils.html import slugify


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
        self.slug = slugify(name, self.settings.get('SLUG_SUBSTITUTIONS', ()))

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

    def __init__(self, name, *args, **kwargs):
        super(Tag, self).__init__(name.strip(), *args, **kwargs)


class Author(URLWrapper):
    pass
