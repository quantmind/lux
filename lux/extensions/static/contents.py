import os
import stat
import json
from functools import partial
from datetime import datetime, date

from dateutil.parser import parse

from lux import template_engine
from lux.extensions.twitter import twitter_card

from .urlwrappers import (Processor, Tag, Author, Category, list_of,
                          Multi, meta_iterator)


METADATA_PROCESSORS = dict(((p.name, p) for p in (
    Processor('name'),
    Processor('title'),
    Processor('slug'),
    Processor('description'),
    Processor('head-title'),
    Processor('head-description'),
    Processor('template'),
    Processor('tag', list_of(Tag), multiple=True),
    Processor('date', lambda x, cfg: [parse(x)]),
    Processor('status'),
    Processor('image-url'),
    Processor('category', list_of(Category), multiple=True),
    Processor('author', list_of(Author), multiple=True),
    Processor('require_css', multiple=True),
    Processor('require_js', multiple=True),
    Processor('require_context', multiple=True),
    Processor('content_type', default='text/html'),
    Processor('draft', lambda x, cfg: json.loads(x)),
    Processor('template-engine',
              default=lambda cfg: cfg['DEFAULT_TEMPLATE_ENGINE']),
    Processor('robots', default=['index', 'follow'], multiple=True),
    Processor('header-image'),
    Processor('twitter-image'),
    Processor('type')
)))


def modified_datetime(src):
    stat_src = os.stat(src)
    return datetime.fromtimestamp(stat_src[stat.ST_MTIME])


class Snippet(object):
    template = None
    template_engine = None
    default_template = None

    def __init__(self, content, metadata, src):
        self._content = content
        self._src = src
        self.modified = modified_datetime(src)
        self.update_meta(metadata)
        self.template = self.template or self.default_template

    def update_meta(self, meta):
        self.__dict__.update(meta_iterator(meta))

    def __repr__(self):
        return self._src
    __str__ = __repr__

    def context(self, app, context=None):
        engine = template_engine(self.template_engine)
        context = context.copy() if context is not None else {}
        ctx = app.extensions['static'].build_info(app)
        for name, value in self.__dict__.items():
            if name.startswith('_'):
                continue
            if value is None:
                value = ''
            if isinstance(value, Multi):
                value = str(value)
            elif isinstance(value, date):
                context['%s_date' % name] = app.format_date(value)
                context[name] = app.format_datetime(value)
                continue
            if value and isinstance(value, str):
                value = engine(value, ctx)
            context[name] = value
        return context

    def render(self, app, context):
        if self.content_type == 'text/html':
            engine = template_engine(self.template_engine)
            context = self.context(app, context)
            content = engine(self._content, context)
            if self.template:
                context['content'] = content
                content = app.render_template(self.template, context=context)
            return content
        else:
            return self._content

    def json_dict(self, app, context):
        '''Convert the snippet into a Json dictionary for the API
        '''
        text = self.render(app, context)
        jd = self.context(app)
        if self.content_type == 'text/html':
            head_des = self.head_description or self.description
            jd.update({'head_title': self.head_title or self.title,
                       'head_description': head_des})
        jd['content'] = text
        return jd

    def html(self, request, context):
        '''Build an HTML5 page for this content
        '''
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
        return self.render(request.app, context)


class Page(Snippet):
    mandatory_properties = ('title',)
    default_template = 'page.html'


class Article(Snippet):
    mandatory_properties = ('title', 'date', 'category')
    default_template = 'article.html'


class Draft(Snippet):
    mandatory_properties = ('title', 'category')
    default_template = 'article.html'


class Quote(Snippet):
    base_properties = ('author', 'date')
