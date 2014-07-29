import os
import stat
import json
from functools import partial
from datetime import datetime

from pulsar.utils.slugify import slugify

from lux import template_engine
from lux.utils import memoized
from lux.extensions.twitter import twitter_card


identity = lambda x, cfg: x

as_list = lambda x, cfg, w=identity: [w(v.strip(), cfg) for v in x.split(',')]


def list_of(W):
    return lambda x, cfg: as_list(x, cfg, W)


class Processor:

    def __init__(self, name, processor=None, default=None, multiple=False):
        self.name = name
        self._default = default
        self.process = processor or as_list
        self.multiple = multiple

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

    def join(self, sep=', '):
        return sep.join(('%s' % v for v in self))


class Single(Multi):

    def value(self):
        return self[0] if self else None


def modified_datetime(src):
    stat_src = os.stat(src)
    return datetime.fromtimestamp(stat_src[stat.ST_MTIME])


def _meta_iterator(meta):
    if meta:
        for n, m in meta.items():
            if isinstance(m, Single):
                m = m[0] if m else None
            yield slugify(n, separator='_'), m


class Snippet(object):
    template = None

    def __init__(self, content, metadata, src):
        self._content = content
        self._src = src
        self.modified = modified_datetime(src)
        self.update_meta(metadata)

    def update_meta(self, meta):
        self.__dict__.update(_meta_iterator(meta))

    def __repr__(self):
        return self._src
    __str__ = __repr__

    def render(self, context):
        if self.content_type == 'text/html':
            return template_engine(self.template)(self._content, context)
        else:
            return self._content

    def json(self, context):
        d = self.json_dict(context)
        return json.dumps(d) if d else None

    def json_dict(self, context):
        if self.content_type == 'text/html':
            text = self.render(context)
            head_des = self.head_description or self.description
            return {'head_title': self.head_title or self.title,
                    'head_description': head_des,
                    'tags': self.tag.join(),
                    'css': self.require_css,
                    'js': self.require_js,
                    'author': self.author.join(),
                    'robots': self.robots.join(),
                    'content': text,
                    'content-type': self.content_type}

    def html(self, request, context):
        '''Build an HTML5 page for this content
        '''
        context = context.copy()
        head = request.html_document.head
        head_title = self.head_title or self.title
        if head_title:
            head.title = head_title
        #
        description = self.head_description or self.description
        if description:
            des = head.replace_meta('description', description)
        if self.tag:
            head.replace_meta("keywords", self.tag.join())
        #
        for css in self.require_css:
            head.links.append(css)
        for js in self.require_js:
            head.scripts.append(js)
        #
        #if 'requirejs' in meta:
        #    head.scripts.require(*meta['requirejs'].split(','))
        #
        if self.author:
            head.replace_meta("author", self.author.join())
        twitter_card(request, **self.__dict__)
        #
        head.add_meta(name='robots', content=self.robots.join())
        return self.render(context)


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
