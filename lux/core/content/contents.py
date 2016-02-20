import os
import stat
import mimetypes
from datetime import datetime, date
from collections import Mapping

from dateutil.parser import parse as parse_date

from pulsar.utils.structures import AttributeDictionary, mapping_iterator
from pulsar.utils.pep import to_string

from lux.utils import iso8601, absolute_uri

from .urlwrappers import (URLWrapper, Processor, MultiValue, Tag, Author,
                          Category)
from ..exceptions import Unsupported
from ..cache import Cacheable, cached


no_draft_field = ('date', 'category')


READERS = {}


CONTENT_EXTENSIONS = {'text/html': 'html',
                      'text/plain': 'txt',
                      'text/css': 'css',
                      'application/json': 'json',
                      'application/javascript': 'js',
                      'application/xml': 'xml'}

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
    Processor('priority', lambda x, cfg: int(x)),
    Processor('order', lambda x, cfg: int(x)),
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


def is_html(content_type):
    return content_type == 'text/html'


def is_text(content_type):
    return content_type in CONTENT_EXTENSIONS


def page_info(data, *include_keys):
    '''Yield only keys which are not associated with a dictionary
    unless they are included in ``included_keys``
    '''
    for key, value in data.items():
        if not isinstance(value, dict) or key in include_keys:
            yield key, value


def register_reader(cls):
    for extension in cls.file_extensions:
        READERS[extension] = cls
    return cls


def get_reader(app, src):
    bits = src.split('.')
    ext = bits[-1] if len(bits) > 1 else None
    Reader = READERS.get(ext) or READERS['']
    if not Reader.enabled:
        raise Unsupported('Missing dependencies for %s' % Reader.__name__)
    return Reader(app, ext)


class ContentFile(Cacheable):
    '''A class for managing a file-based content
    '''
    suffix = None

    def __init__(self, src, path=None, model=None, **params):
        self.src = src
        self.path = path
        self.model = model
        self.meta = AttributeDictionary(params)

    def __repr__(self):
        return self.src
    __str__ = __repr__

    @property
    def content_type(self):
        ct, _ = mimetypes.guess_type(self.src)
        return ct

    def cache_key(self, app):
        return self.src


class HtmlContentFile(ContentFile):
    suffix = 'html'
    template = None

    def __repr__(self):
        return self.src
    __str__ = __repr__

    @property
    def content_type(self):
        return 'text/html'

    @cached
    def json(self, request):
        """Convert the content into a Json dictionary for the API
        """
        app = request.app
        context = app.context(request)
        if self.model:
            self.model.context(request, self, context)
        #
        self.meta.modified = modified_datetime(self.src)
        data = self._to_json(request, self.meta)
        text = data.get(self.suffix) or {}
        data[self.suffix] = text
        text['main'] = self.render(app, context)
        #
        head = {}
        for key in HEAD_META:
            value = data.get(key)
            if value:
                head[key] = value
        #
        if 'head' in data:
            head.update(data['head'])

        data['ext'] = self.suffix
        data['path'] = self.path
        data['head'] = head
        if self.model:
            self.model.json(request, self, data)
        return data

    def render(self, app, context):
        """Render this content with a context dictionary

        :param app: lux application
        :param context: context dictionary
        :return: an HTML string
        """
        content, meta = get_reader(app, self.src).read(self.src)
        self.meta.update(meta)
        context = context if context is not None else {}
        context.update(self._flatten(self.meta))
        render = app.template_engine(self.meta.template_engine)
        content = render(content, context)
        if self.meta.template:
            template = app.template_full_path(self.meta.template)
            if template:
                context['%s_main' % self.suffix] = content
                with open(template, 'r') as file:
                    template_str = file.read()
                content = render(template_str, context)
        return content

    def html(self, request):
        '''Build the ``html_main`` key for this content and set
        content specific values to the ``head`` tag of the
        HTML5 document.
        '''
        # The JSON data for this page
        data = self.json(request)
        doc = request.html_document
        doc.jscontext['page'] = dict(page_info(data))
        #
        image = absolute_uri(request, data.get('image'))
        doc.meta.update({'og:image': image,
                         'og:published_time': data.get('date'),
                         'og:modified_time': data.get('modified')})
        doc.meta.update(data['head'])
        #
        if not request.config.get('HTML5_NAVIGATION'):
            for css in data.get('require_css') or ():
                doc.head.links.append(css)
            doc.head.scripts.require.extend(data.get('require_js') or ())
        #
        if request.cache.uirouter is False:
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
        meta.site = {}
        for name in ('template_engine', 'template'):
            default = getattr(self, name)
            value = metadata.pop(name, default)
            meta.site[name] = value
            setattr(self, name, value)

        context = self.context(self.app.config)
        self._engine = self._app.template_engine(self.template_engine)
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
            raise ValueError('A dictionary found when converting to string')
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
        elif isinstance(value, str):
            return self._engine(to_string(value), context)
        else:
            return value

    def _to_json(self, request, value):
        if isinstance(value, Mapping):
            return dict(((k, self._to_json(request, v))
                         for k, v in value.items()))
        elif isinstance(value, (list, tuple)):
            return [self._to_json(request, v) for v in value]
        elif isinstance(value, date):
            return iso8601(value)
        elif isinstance(value, URLWrapper):
            return value.to_json(request)
        else:
            return value
