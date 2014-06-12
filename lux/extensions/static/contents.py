import os
import stat
from functools import partial
from datetime import datetime

from lux.utils import memoized
from lux.extensions.twitter import twitter_card

from .urlwrappers import Tag, Author, Category


meta_properties = ('js', 'css')

def modified_datetime(src):
    stat_src = os.stat(src)
    return datetime.fromtimestamp(stat_src[stat.ST_MTIME])


class Snippet(object):
    keys = ('main',)

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

    def html(self, request):
        '''Build an HTML5 page for this content
        '''
        meta = self._metadata
        head = request.html_document.head
        title = meta.get('title')
        head_title = meta.get('head-title') or title
        if head_title:
            head.title = head_title
        #
        description = (meta.get('head-description') or meta.get('summary') or
                       meta.get('description'))
        if description:
            des = head.replace_meta('description', description)
        if 'tags' in meta:
            tags = meta['tags']
            head.replace_meta("keywords", ', '.join((str(t) for t in tags)))
        #
        if 'css' in meta:
            for css in meta['css'].split(','):
                head.links.append(css.strip())
        if 'js' in meta:
            for script in meta['js'].split(','):
                head.scripts.append(script.strip())
        if 'requirejs' in meta:
            head.scripts.require(*meta['requirejs'].split(','))
        #
        author = meta.get('author')
        if author:
            head.replace_meta("author", str(author))
        twitter_card(request, **meta)
        #
        robots = meta.get('robots') or 'index, follow'
        head.add_meta(name='robots', content=robots)
        for key in self.keys:
            attrname = 'html_%s' % key
            if hasattr(self, attrname):
                yield (key, getattr(self, attrname)(request))

    def html_main(self, request):
        '''Return the content to '''
        return self._content


for meta_property in meta_properties:
    setattr(Snippet, meta_property, property(
        lambda self: self._metadata.get(meta_property)))


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
