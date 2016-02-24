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
    Processor('title'),
    Processor('description'),
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

    def __init__(self, src, **params):
        self.src = src
        self.model = params.pop('model', None)
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
        """Convert the content into a JSON dictionary for the API
        """
        self.meta.modified = modified_datetime(self.src)
        app = request.app
        #
        # Get context dictionary from application and model if available
        context = app.context(request)
        if self.model:
            self.model.context(request, self, context)
        #
        self.meta['html_main'] = self.render(app, context)
        return dict(self.meta)

    def html(self, request):
        '''Build the ``html_main`` key for this content and set
        content specific values to the ``head`` tag of the
        HTML5 document.
        '''
        # The JSON data for this page
        data = self.json(request)
        doc = request.html_document
        #
        image = absolute_uri(request, data.get('image'))
        doc.meta.update({'og:image': image,
                         'og:published_time': data.get('date'),
                         'og:modified_time': data.get('modified')})
        head = {}
        page = {}
        for key, value in data.items():
            bits = key.split('_')
            N = len(bits)
            if N > 1 and bits[0] == 'head':
                key = '_'.join(bits[1:])
                head[key] = value
                doc.meta.set('_'.join(bits[1:]), value)
            elif N == 1:
                page[key] = value

        # Add head keys if needed
        for key in HEAD_META:
            if key not in head and key in data:
                doc.meta.set(key, data[key])

        doc.jscontext['page'] = page
        return data['html_main']

    def render(self, app, context):
        """Render this content with a context dictionary

        :param app: lux application
        :param context: context dictionary
        :return: an HTML string
        """
        context = context if context is not None else {}
        render = app.template_engine(self.meta.template_engine)
        content, meta = get_reader(app, self.src).read(self.src)
        self.meta.update(meta)
        meta = dict(self._flatten(self.meta))
        context.update(meta)
        self.meta = AttributeDictionary(self._render_data(app, meta, render,
                                                          context))
        context.update(self.meta)
        #
        content = render(content, context)
        if self.meta.template:
            template = app.template_full_path(self.meta.template)
            if template:
                context['%s_main' % self.suffix] = content
                with open(template, 'r') as file:
                    template_str = file.read()
                content = render(template_str, context)
        return content

    # INTERNALS
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

    def _render_data(self, request, value, render, context):
        if isinstance(value, Mapping):
            return dict(((k, self._render_data(request, v, render, context))
                         for k, v in value.items()))
        elif isinstance(value, (list, tuple)):
            return [self._render_data(request, v, render, context)
                    for v in value]
        elif isinstance(value, date):
            return iso8601(value)
        elif isinstance(value, URLWrapper):
            return value.to_json(request)
        elif isinstance(value, str):
            return render(value, context)
        else:
            return value
