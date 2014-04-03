import os
import stat
from functools import partial
from datetime import datetime

from lux.utils import memoized

from .urlwrappers import Tag, Author, Category


def modified_datetime(src):
    stat_src = os.stat(src)
    return datetime.fromtimestamp(stat_src[stat.ST_MTIME])


class Snippet(object):

    def __init__(self, content, metadata=None, src=None, dst=None):
        self._content = content
        self._metadata = metadata if metadata is not None else {}
        self._src = src
        self._dst = dst
        if src:
            self._metadata['modified'] = modified_datetime(src)

    def __repr__(self):
        return self._content
    __str__ = __repr__

    @property
    def content_type(self):
        return self._metadata.get('content_type', 'text/html')

    @property
    def date(self):
        return self._metadata.get('date')

    @property
    def title(self):
        return self._metadata.get('title')

    @property
    def modified(self):
        return self._metadata.get('modified')

    @property
    def draft(self):
        return self._metadata.get('draft')


class Page(Snippet):
    mandatory_properties = ('title',)
    default_template = 'page'


class Article(Snippet):
    mandatory_properties = ('title', 'date', 'category')
    default_template = 'article'


class Draft(Snippet):
    mandatory_properties = ('title', 'category')
    default_template = 'article'


class Quote(Snippet):
    base_properties = ('author', 'date')
