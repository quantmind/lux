import os
import stat
import mimetypes
from datetime import datetime, date
from collections import Mapping

from dateutil.parser import parse as parse_date

from pulsar import Unsupported
from pulsar.utils.structures import mapping_iterator
from pulsar.apps.wsgi import file_response
from pulsar.utils.httpurl import CacheControl

from lux.utils import iso8601, absolute_uri

from .urlwrappers import (URLWrapper, Processor, MultiValue, Tag, Author,
                          Category)
from ..cache import Cacheable


no_draft_field = ('date', 'category')


READERS = {}


CONTENT_EXTENSIONS = {'text/html': 'html',
                      'text/plain': 'txt',
                      'text/css': 'css',
                      'application/json': 'json',
                      'application/javascript': 'js',
                      'application/xml': 'xml'}

HEAD_META = frozenset(('title', 'description', 'author', 'keywords'))


METADATA_PROCESSORS = dict(((p.name, p) for p in (
    Processor('title'),
    Processor('description'),
    Processor('image'),
    Processor('date', lambda x, cfg: get_date(x)),
    Processor('modified', lambda x, cfg: get_date(x)),
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


def get_date(d):
    if not isinstance(d, date):
        d = parse_date(d)
    return d


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
    return Reader(app.app, ext)


def render_data(app, value, render, context):
    if isinstance(value, Mapping):
        return dict(((k, render_data(app, v, render, context))
                     for k, v in value.items()))
    elif isinstance(value, (list, tuple)):
        return [render_data(app, v, render, context) for v in value]
    elif isinstance(value, date):
        return iso8601(value)
    elif isinstance(value, URLWrapper):
        return value.to_json(app)
    elif isinstance(value, str):
        return render(value, context)
    else:
        return value


class ContentFile:
    """A class for managing a file-based content
    """
    cache_control = CacheControl(maxage=86400)

    def __init__(self, src, content_type=None, cache_control=None):
        self.src = src
        self.content_type = content_type or mimetypes.guess_type(src)[0]
        self.cache_control = cache_control or self.cache_control

    def __repr__(self):
        return self.src
    __str__ = __repr__

    def response(self, request):
        return file_response(request, self.src,
                             content_type=self.content_type,
                             cache_control=self.cache_control)


class HtmlFile(Cacheable):
    suffix = 'html'

    def __init__(self, src, **params):
        self.src = src
        self.model = params.pop('model', None)
        self.meta = params

    def __repr__(self):
        return self.src
    __str__ = __repr__

    @property
    def content_type(self):
        return 'text/html'

    def cache_key(self, app):
        return self.src

    def render(self, app, context):
        render = app.template_engine(self.meta.template_engine)
        with open(self.src, 'r') as file:
            template_str = file.read()
        return render(template_str, context)


class HtmlContentFile(HtmlFile):
    template = None

    def __repr__(self):
        return self.src
    __str__ = __repr__

    @property
    def content_type(self):
        return 'text/html'

    def json(self, request):
        """Convert the content into a JSON dictionary
        """
        app = request.app
        meta = self.meta.copy()
        meta['modified'] = modified_datetime(self.src)
        content, meta = get_reader(app, self.src).read(self.src, meta)
        render = app.template_engine(meta.get('template_engine'))
        context = app.config.copy()
        context.update(meta)
        meta = render_data(app, meta, render, context)
        meta['body'] = content
        return dict(_flatten(meta))


def html(request, meta):
    """Build the ``html_main`` key for this content and set
    content specific values to the ``head`` tag of the
    HTML5 document.
    """
    doc = request.html_document
    app = request.app
    content = meta.get('body')
    template = meta.get('template')
    context = app.context(request)
    if template:
        context['html_main'] = content
        content = app.render_template(template, context,
                                      engine=meta.get('template_engine'))
    #
    image = absolute_uri(request, meta.get('image'))
    doc.meta.update({'og:image': image,
                     'og:published_time': meta.get('date'),
                     'og:modified_time': meta.get('modified')})
    #
    # Add head keys
    head = {}
    page = {}
    for key, value in meta.items():
        bits = key.split('_', 1)
        if len(bits) == 2 and bits[0] == 'head':
            key = bits[1].replace('__', ':')
            head[key] = value
            doc.meta.set(key, value)
        else:
            page[key] = value

    # Add head keys if needed
    for key in HEAD_META:
        if key not in head and key in meta:
            doc.meta.set(key, meta[key])

    doc.jscontext['page'] = page
    return content


# INTERNALS
def _flatten(meta):
    for key, value in mapping_iterator(meta):
        if isinstance(value, Mapping):
            for child, v in _flatten(value):
                yield '%s_%s' % (key, child), v
        else:
            yield key, _flatten_value(value)


def _flatten_value(value):
    if isinstance(value, Mapping):
        raise ValueError('A dictionary found when converting to string')
    elif isinstance(value, (list, tuple)):
        return ', '.join(str(_flatten_value(v)) for v in value)
    elif isinstance(value, date):
        return iso8601(value)
    elif isinstance(value, URLWrapper):
        return str(value)
    else:
        return value
