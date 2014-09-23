import os
import stat
import json
from functools import partial
from datetime import datetime, date

from dateutil.parser import parse as parse_date

import pulsar
from pulsar.utils.slugify import slugify

from lux import template_engine, JSON_CONTENT_TYPES

from .urlwrappers import (Processor, Tag, Author, Category, list_of,
                          Multi, meta_iterator)


class SkipBuild(pulsar.Http404):
    pass


class BuildError(pulsar.Http404):
    pass

no_draft_field = ('date', 'category')

CONTENT_EXTENSIONS = {'text/html': 'html',
                      'text/plain': 'txt',
                      'application/json': 'json'}


METADATA_PROCESSORS = dict(((p.name, p) for p in (
    Processor('name'),
    Processor('slug'),
    Processor('title'),
    Processor('description'),
    Processor('tag', list_of(Tag), multiple=True),
    Processor('date', lambda x, cfg: [parse_date(x)]),
    Processor('status'),
    Processor('priority'),
    Processor('category', list_of(Category), multiple=True),
    Processor('author', list_of(Author), multiple=True),
    Processor('require_css', multiple=True),
    Processor('require_js', multiple=True),
    Processor('require_context', multiple=True),
    Processor('content_type', default='text/html'),
    Processor('template'),
    Processor('template-engine',
              default=lambda cfg: cfg['DEFAULT_TEMPLATE_ENGINE']),
    Processor('robots', default=['index', 'follow'], multiple=True),
    Processor('type')
)))


def modified_datetime(src):
    stat_src = os.stat(src)
    return datetime.fromtimestamp(stat_src[stat.ST_MTIME])


def is_text(content_type):
    return content_type in CONTENT_EXTENSIONS


class Snippet(object):
    template = None
    template_engine = None
    default_template = None
    mandatory_properties = ()

    def __init__(self, content, metadata, src, path=None, context=None,
                 **params):
        self._json_content = None
        self._content = content
        self._context_for = context
        self._additional_context = {}
        self._src = src
        self._path = path or src
        self._name = self._path
        self.modified = modified_datetime(src)
        self.update_meta(metadata, params)
        if is_text(self.content_type):
            dir, slug = os.path.split(self._path)
            if not slug:
                slug = self._name
                dir = None
            self._name = slugify(self._name, separator='_')
            if not self.slug:
                self.slug = slugify(slug, separator='_')
            if dir:
                self.slug = '%s/%s' % (dir, self.slug)
        elif not self.slug:
            self.slug = self._name
        self.template = self.template or self.default_template

    @property
    def name(self):
        return self._name

    @property
    def suffix(self):
        return CONTENT_EXTENSIONS.get(self.content_type)

    @property
    def path(self):
        return self._path

    @property
    def reldate(self):
        return self.date or self.modified

    @property
    def year(self):
        return self.reldate.year

    @property
    def month(self):
        return self.reldate.month

    @property
    def month2(self):
        return self.reldate.strftime('%m')

    @property
    def month3(self):
        return self.reldate.strftime('%b').lower()

    @property
    def id(self):
        if is_text(self.content_type):
            return '%s.json' % self.slug

    @property
    def context_for(self):
        '''A list of contents names for which this snippet is required
        in the context dictionary
        '''
        return self._context_for

    @property
    def additional_context(self):
        '''Dictionary of key and :class:`.Snippet` providing additional
        keys for this content
        '''
        return self._additional_context

    def __repr__(self):
        return self._src
    __str__ = __repr__

    def key(self, name=None):
        '''The key for a context dictionary
        '''
        suffix = self.suffix
        name = name or self._name
        return '%s_%s' % (suffix, name) if suffix else name

    def update_meta(self, meta, params=None):
        self.__dict__.update(meta_iterator(meta, params))

    def context(self, app, names=None, context=None):
        '''Extract a context dictionary from this snippet.
        '''
        all_names = names if names is not None else self.__dict__
        if context is None:
            context = app.extensions['static'].build_info(app)
        ctx = context
        context = context.copy()
        engine = template_engine(self.template_engine)
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
            elif isinstance(value, dict):
                if not value:
                    continue
                for k, val in tuple(value.items()):
                    if isinstance(val, (list, tuple)):
                        value[k] = tuple((engine(v, ctx) for v in val))
                    else:
                        value[k] = engine(val, ctx)
            if value and isinstance(value, str):
                value = engine(value, ctx)
            context[name] = value
        #
        if names is None:
            #
            #    Check for missing properties
            for name in self.mandatory_properties:
                if not context.get(name):
                    raise BuildError("Property '%s' not available in %s"
                                     % (name, self))
        #
        return context

    def render(self, app, context):
        '''Render the snippet
        '''
        if is_text(self.content_type):
            engine = template_engine(self.template_engine)
            context = self.context(app, context=context)
            content = engine(self._content, context)
            if self.template:
                context['html_main'] = content
                content = app.render_template(self.template, context=context)
            return content
        else:
            return self._content

    def json_dict(self, app, context):
        '''Convert the content into a Json dictionary for the API
        '''
        if not self._json_content and is_text(self.content_type):
            jd = self.context(app)
            context.update(jd)
            #
            # Add additional context keys
            if self.additional_context:
                for key, ct in self.additional_context.items():
                    context[ct.key(key)] = ct.render(app, context)
            #
            key = self.key('main')
            jd[key] = self.render(app, context)
            if self.content_type == 'text/html':
                head = jd.get('head')
                if not head:
                    head = {}
                    jd['head'] = head
                head.update({'title': self.title,
                             'description': self.description})

            self._json_content = jd
        return self._json_content

    def html(self, request, context):
        '''Build the ``html_main`` key for this content and set
        content specific values to the ``head`` tag of the
        HTML5 document.
        '''
        assert self.content_type == 'text/html', '%s not html' % self
        data = self.json_dict(request.app, context)
        context.update(data)
        doc = request.html_document
        head = doc.head
        #
        head.fields.update(data['head'])
        if 'html_url' in data:
            head.fields.set_private('html_url', data['html_url'])
        #
        require_css = data.get('require_css', '')
        if require_css:
            for css in require_css.split(','):
                head.links.append(css)
        require_js = data.get('require_js', '')
        if require_js:
            for js in require_js.split(','):
                head.scripts.require(js)
        #
        author = data.get('author')
        if author:
            head.replace_meta('author', author)
        #twitter_card(request, **data)
        #
        robots = data.get('robots')
        if robots:
            head.add_meta(name='robots', content=robots)
        self.on_html(request.app, doc)
        return context.get(self.key('main'))

    def on_html(self, app, doc):
        pass

    @classmethod
    def as_draft(cls):
        mp = tuple((a for a in cls.mandatory_properties
                    if a not in no_draft_field))
        return cls.__class__('Draft', (cls,), {'mandatory_properties': mp})


class Article(Snippet):
    mandatory_properties = ('title', 'date', 'category')
    default_template = 'article.html'


class Quote(Snippet):
    base_properties = ('author', 'date')
