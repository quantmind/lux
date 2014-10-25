import os
import stat
import json
from functools import partial
from datetime import datetime, date
from collections import Mapping

from dateutil.parser import parse as parse_date

import pulsar
from pulsar import HttpException, Http404
from pulsar.utils.slugify import slugify
from pulsar.utils.structures import AttributeDictionary, mapping_iterator
from pulsar.utils.pep import to_string
from pulsar.apps.wsgi import Links

from lux import JSON_CONTENT_TYPES
from lux.utils import iso8601
from lux.extensions.ui import CssLibraries

from .urlwrappers import Processor, MultiValue, Tag, Author, Category


class SkipBuild(Http404):
    pass


class BuildError(Http404):
    pass


class Unsupported(HttpException):
    status = 415


no_draft_field = ('date', 'category')

CONTENT_EXTENSIONS = {'text/html': 'html',
                      'text/plain': 'txt',
                      'application/json': 'json'}

HEAD_META = ('title', 'description', 'author', 'keywords')

METADATA_PROCESSORS = dict(((p.name, p) for p in (
    Processor('name'),
    Processor('slug'),
    Processor('title'),
    # Description, if not head_description available it will also be used as
    # description in head meta.
    Processor('description'),
    # An optional image url which can be used to identify the page
    Processor('image'),
    Processor('date', lambda x, cfg: parse_date(x)),
    Processor('status'),
    Processor('priority'),
    MultiValue('keywords', Tag),
    MultiValue('category', Category),
    MultiValue('author', Author),
    MultiValue('require_css'),
    MultiValue('require_js'),
    MultiValue('require_context'),
    Processor('content_type'),
    Processor('template'),
    Processor('template-engine')
)))


def modified_datetime(src):
    stat_src = os.stat(src)
    return datetime.fromtimestamp(stat_src[stat.ST_MTIME])


def is_text(content_type):
    return content_type in CONTENT_EXTENSIONS


def page_info(data):
    for key, value in data.items():
        if not isinstance(value, dict):
            yield key, value


class Content(object):
    template = None
    template_engine = None
    _json_dict = None
    '''Template engine to render this content. Overwritten my metadata.
    If not available, the application default engine is used'''
    mandatory_properties = ()

    def __init__(self, app, content, metadata, src, path=None, context=None,
                 **params):
        self._app = app
        self._content = content
        self._context_for = context
        self._additional_context = {}
        self._src = src
        self._path = path or src
        self._meta = AttributeDictionary(params)
        if src:
            self._meta.modified = modified_datetime(src)
        else:
            self._meta.modified = datetime.now()
        # Get the site meta data dictionary.
        # Used to render Content metadata
        self._update_meta(metadata)
        meta = self._meta
        if self.is_text:
            dir, slug = os.path.split(self._path)
            if not slug:
                slug = self._path
                dir = None
            if not meta.slug:
                meta.slug = slugify(slug, separator='_')
            if dir:
                meta.slug = '%s/%s' % (dir, meta.slug)
        elif not meta.slug:
            meta.slug = self._path
        meta.name = slugify(meta.slug, separator='_')
        for name in self.mandatory_properties:
            if not meta.get(name):
                raise BuildError("Property '%s' not available in %s"
                                 % (name, self))

    @property
    def name(self):
        return self._meta.name

    @property
    def content_type(self):
        return self._meta.content_type

    @property
    def is_text(self):
        return self._meta.content_type in CONTENT_EXTENSIONS

    @property
    def is_html(self):
        return self._meta.content_type == 'text/html'

    @property
    def suffix(self):
        return CONTENT_EXTENSIONS.get(self._meta.content_type)

    @property
    def path(self):
        return self._path

    @property
    def reldate(self):
        return self._meta.date or self._meta.modified

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
        if self.is_text:
            return '%s.json' % self._meta.slug

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
        name = name or self.name
        return '%s_%s' % (suffix, name) if suffix else name

    def context(self, context=None):
        '''Extract the context dictionary for server side template rendering
        '''
        ctx = dict(self._flatten(self._meta))
        if context:
            ctx.update(context)
        return ctx

    def urlparams(self, names=None):
        urlparams = {}
        if names:
            for name in names:
                value = self._meta.get(name) or getattr(self, name, None)
                if value in (None, ''):
                    if name == 'id':
                        raise SkipBuild
                    elif names:
                        raise KeyError("%s could not obtain url variable '%s'"
                                       % (self, name))
                urlparams[name] = value
        return urlparams

    def render(self, context):
        '''Render the content
        '''
        if self.is_text:
            context = self.context(context)
            content = self._engine(self._content, context)
            if self.template:
                context[self.key('main')] = content
                content = self._app.render_template(self.template,
                                                    context=context)
            return content
        else:
            return self._content

    def json(self, request):
        '''Convert the content into a Json dictionary for the API
        '''
        if not self._json_dict and self.is_text:
            context = self._app.context(request)
            context = self.context(context)
            # Add additional context keys
            if self.additional_context:
                for key, ct in self.additional_context.items():
                    context[ct.key(key)] = ct.render(context)
            #
            assert self.suffix
            data = self._to_json(self._meta)
            text = data.get(self.suffix) or {}
            data[self.suffix] = text
            text['main'] = self.render(context)
            #
            head = {}
            for key in HEAD_META:
                value = data.get(key)
                if value:
                    head[key] = value
            #
            require_css = data.get('require_css')
            if require_css:
                data['require_css'] = []
                cfg = request.config
                links = Links(cfg['MEDIA_URL'],
                              minified=cfg['MINIFIED_MEDIA'])
                for css in require_css:
                    css = CssLibraries.get(css, css)
                    links.append(css)
                for link in links.children:
                    link = link.split("href=")
                    if len(link) == 2:
                        href = link[1]
                        c = href[0]
                        href = href[1:]
                        link = href[:href.find(c)]
                        data['require_css'].append(link)
            #
            if 'head' in data:
                head.update(data['head'])

            data['head'] = head
            self._json_dict = data
        return self._json_dict

    def html(self, request):
        '''Build the ``html_main`` key for this content and set
        content specific values to the ``head`` tag of the
        HTML5 document.
        '''
        if not self.is_html:
            raise Unsupported
        # The JSON data for this page
        data = self.json(request)
        doc = request.html_document
        doc.jscontext['page'] = dict(page_info(data))
        #
        doc.meta.update({'og:image': data.get('image'),
                         'og:published_time': data.get('date'),
                         'og:modified_time': data.get('modified')})
        doc.meta.update(data['head'])
        #
        if not request.config['ANGULAR_UI_ROUTER']:
            for css in data.get('require_css') or ():
                doc.head.links.append(css)
            doc.head.scripts.require.extend(data.get('require_js') or ())
        self.on_html(doc)
        return data[self.suffix]['main']

    def on_html(self, doc):
        pass

    @classmethod
    def as_draft(cls):
        mp = tuple((a for a in cls.mandatory_properties
                    if a not in no_draft_field))
        return cls.__class__('Draft', (cls,), {'mandatory_properties': mp})

    # INTERNALS
    def _update_meta(self, metadata):
        meta = self._meta
        meta.site = self._app.extensions['static'].build_info(self._app)
        context = self.context()
        for name in ('template_engine', 'template'):
            default = getattr(self, name)
            value = metadata.pop(name, default)
            meta.site[name] = value
            setattr(self, name, value)
        self._engine = engine = self._app.template_engine(self.template_engine)
        meta.update(((key, self._render_meta(value, context))
                    for key, value in metadata.items()))

    def _flatten(self, meta):
        for key, value in mapping_iterator(meta):
            if isinstance(value, Mapping):
                for child, value in self._flatten(value):
                    yield '%s_%s' % (key, child), value
            else:
                yield key, self._to_string(value)

    def _to_string(self, value):
        if isinstance(value, Mapping):
            raise BuildError('A dictionary found when coverting to string')
        elif isinstance(value, (list, tuple)):
            return ', '.join(self._to_string(v) for v in value)
        elif isinstance(value, date):
            return iso8601(value)
        else:
            return to_string(value)

    def _render_meta(self, value, context):
        if isinstance(value, Mapping):
            return dict(((k, self._render_meta(v, context))
                          for k, v in value.items()))
        elif isinstance(value, (list, tuple)):
            return [self._render_meta(v, context) for v in value]
        elif isinstance(value, date):
            return value
        elif value is not None:
            return self._engine(to_string(value), context)

    def _to_json(self, value):
        if isinstance(value, Mapping):
            return dict(((k, self._to_json(v)) for k, v in value.items()))
        elif isinstance(value, (list, tuple)):
            return [self._to_json(v) for v in value]
        elif isinstance(value, date):
            return iso8601(value)
        else:
            return value


class Article(Content):
    mandatory_properties = ('title', 'date', 'category')
    template = 'article.html'
