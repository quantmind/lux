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


CONTENT_EXTENSIONS = {'text/html': 'html',
                      'text/plain': 'txt',
                      'application/json': 'json'}


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
    return content_type[:5] == 'text/' or content_type == 'application/json'


class Snippet(object):
    template = None
    template_engine = None
    default_template = None
    mandatory_properties = ()

    def __init__(self, content, metadata, src, path=None, context=None):
        self._json_content = None
        self._content = content
        self._context = context
        self.modified = modified_datetime(src)
        self.update_meta(metadata)
        self._src = src
        self._path = path or src
        self._name = path
        if is_text(self.content_type):
            self._name = slugify(self._name, separator='_')
            if not self.slug:
                self.slug = slugify(self.title or self._name, separator='_')
        elif not self.slug:
            self.slug = self._name
        self.template = self.template or self.default_template

    @property
    def name(self):
        return self._name

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
            #    Check for missing properties
            for name in self.mandatory_properties:
                assert context.get(name), ("Property '%s' not available in %s"
                                           % (name, self))
        #
        return context

    def render(self, app, context):
        '''Render the snippet
        '''
        if self.content_type == 'text/html':
            engine = template_engine(self.template_engine)
            context = self.context(app, context=context)
            content = engine(self._content, context)
            if self.template:
                context['main'] = content
                content = app.render_template(self.template, context=context)
            return content
        else:
            return self._content

    def json_dict(self, app, context):
        '''Convert the content into a Json dictionary for the API
        '''
        if not self._json_content and is_text(self.content_type):
            text = self.render(app, context)
            jd = self.context(app)

            ext = CONTENT_EXTENSIONS[self.content_type]
            jd[ext] = content = {}
            if self.content_type == 'text/html':
                head_des = self.head_description or self.description
                jd.update({'head_title': self.head_title or self.title,
                           'head_description': head_des})
            content['main'] = text
            #
            # Add additional context keys
            if self._context:
                for key, target in self._context.items():
                    if target not in context:
                        app.logger.warning("Cannot find '%s' key '%s'"
                                           " in '%s' context"
                                           % (key, target, self))
                    else:
                        content[key] = context[target]
            self._json_content = jd
        return self._json_content

    def html(self, request, context):
        '''Build an HTML5 page for this content
        '''
        assert self.content_type == 'text/html', '%s not html' % self
        data = self.json_dict(request.app, context)
        context.update(data['html'])
        head = request.html_document.head
        #
        if 'head_title' in data:
            head.title = data['head_title']
        #
        if 'head_description' in data:
            des = head.replace_meta('description', data['head_description'])
        if 'tag' in data:
            head.replace_meta("keywords", data['tag'])
        #
        for css in self.require_css:
            head.links.append(css)
        for js in self.require_js:
            head.scripts.append(js)
        #
        #if 'requirejs' in meta:
        #    head.scripts.require(*meta['requirejs'].split(','))
        #
        if 'author' in data:
            head.replace_meta("author", data['author'])
        twitter_card(request, **data)
        #
        if 'robots' in data:
            head.add_meta(name='robots', content=data['robots'])
        return context.pop('main')


class Article(Snippet):
    mandatory_properties = ('title', 'date', 'category')
    default_template = 'article.html'


class Draft(Snippet):
    mandatory_properties = ('title', 'category')
    default_template = 'article.html'


class Quote(Snippet):
    base_properties = ('author', 'date')
