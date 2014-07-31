import os
import stat
import json
from functools import partial
from datetime import datetime, date

from dateutil.parser import parse as parse_date

from pulsar.utils.slugify import slugify

from lux import template_engine, JSON_CONTENT_TYPES
from lux.extensions.twitter import twitter_card

from .urlwrappers import (Processor, Tag, Author, Category, list_of,
                          Multi, meta_iterator)


class SkipBuild(Exception):
    pass


METADATA_PROCESSORS = dict(((p.name, p) for p in (
    Processor('name'),
    Processor('title'),
    Processor('slug'),
    Processor('description'),
    Processor('head-title'),
    Processor('head-description'),
    Processor('template'),
    Processor('tag', list_of(Tag), multiple=True),
    Processor('date', lambda x, cfg: [parse_date(x)]),
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


def is_text(content_type):
    return content_type[:5] == 'text/' or content_type in JSON_CONTENT_TYPES


class Snippet(object):
    template = None
    template_engine = None
    default_template = None
    mandatory_properties = ()

    def __init__(self, content, metadata, src, path=None):
        self._content = content
        self._src = src
        self._path = path or src
        self._name = slugify(path, separator='_')
        self.modified = modified_datetime(src)
        self.update_meta(metadata)
        self.template = self.template or self.default_template
        if not self.slug:
            self.slug = slugify(self.title or self._name, separator='_')

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def year(self):
        return self.date.year if self.date else None

    @property
    def month(self):
        return self.date.month if self.date else None

    @property
    def month2(self):
        return self.date.strftime('%m') if self.date else None

    @property
    def month3(self):
        return self.date.strftime('%b').lower() if self.date else None

    @property
    def id(self):
        if is_text(self.content_type):
            return '%s.json' % self.slug

    def __repr__(self):
        return self._src
    __str__ = __repr__

    def update_meta(self, meta):
        self.__dict__.update(meta_iterator(meta))

    def context(self, app, names=None, context=None):
        '''Extract a context dictionary from this snippet.
        '''
        all_names = names if names is not None else self.__dict__
        context = context.copy() if context is not None else {}
        engine = template_engine(self.template_engine)
        ctx = app.extensions['static'].build_info(app)
        #
        for name in all_names:
            if name.startswith('_'):
                continue
            value = getattr(self, name, None)
            if value is None:
                if name == 'id':
                    raise SkipBuild
                elif names:
                    raise KeyError("%s could not obtain url variable '%s'" %
                                   (self, name))
                else:
                    value = ''
            elif isinstance(value, Multi):
                value = str(value)
            elif isinstance(value, date):
                context['%s_date' % name] = app.format_date(value)
                context[name] = app.format_datetime(value)
                continue
            if value and isinstance(value, str):
                value = engine(value, ctx)
            context[name] = value
        #
        if names is None:
            #
            #    Check for missing properties
            for name in self.mandatory_properties:
                assert context.get(name), ("Property '%s' not available in %s"
                                           % (name, self))
        #
        return context

    def render(self, app, context):
        if self.content_type == 'text/html':
            engine = template_engine(self.template_engine)
            context = self.context(app, context=context)
            content = engine(self._content, context)
            if self.template:
                context['content'] = content
                content = app.render_template(self.template, context=context)
            return content
        else:
            return self._content

    def json_dict(self, app, context):
        '''Convert the content into a Json dictionary for the API
        '''
        if is_text(self.content_type):
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
        assert self.content_type == 'text/html', '%s not html' % self
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


class Article(Snippet):
    mandatory_properties = ('title', 'date', 'category')
    default_template = 'article.html'


class Draft(Snippet):
    mandatory_properties = ('title', 'category')
    default_template = 'article.html'


class Quote(Snippet):
    base_properties = ('author', 'date')
