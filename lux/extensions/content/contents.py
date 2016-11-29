import os
import stat
from datetime import datetime, date
from collections import Mapping
from itertools import chain

from dateutil.parser import parse as parse_date

from pulsar import Unsupported
from pulsar.utils.slugify import slugify
from pulsar.utils.structures import mapping_iterator

from lux.utils.date import iso8601

from .urlwrappers import (URLWrapper, Processor, MultiValue, Tag, Author,
                          Category)

try:
    from markdown import Markdown
except ImportError:     # pragma    nocover
    Markdown = False


def chain_meta(meta1, meta2):
    return chain(mapping_iterator(meta1), mapping_iterator(meta2))


def guess(value):
    return value if len(value) > 1 else value[-1]


READERS = {}
# Meta attributes to contribute to html head tag
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
    Processor('template'),
    Processor('template-engine'),
    MultiValue('requirejs')
)))


def get_date(d):
    if not isinstance(d, date):
        d = parse_date(d)
    return d


def modified_datetime(src):
    stat_src = os.stat(src)
    return datetime.fromtimestamp(stat_src[stat.ST_MTIME])


def register_reader(cls):
    for extension in cls.file_extensions:
        READERS[extension] = cls
    return cls


def get_reader(app, src=None, ext=None):
    if src:
        bits = src.split('.')
        ext = bits[-1] if len(bits) > 1 else None
    reader = READERS.get(ext) or READERS['html']
    if not reader or not reader.enabled:
        name = reader.__name__ if reader else ext
        raise Unsupported('Missing dependencies for %s' % name)
    return reader(app.app, ext)


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


def process_meta(meta, cfg):
    as_list = MultiValue()
    for key, values in mapping_iterator(meta):
        key = slugify(key, separator='_')
        if not isinstance(values, (list, tuple)):
            values = (values,)
        if key not in METADATA_PROCESSORS:
            bits = key.split('_', 1)
            values = guess(as_list(values, cfg))
            if len(bits) > 1 and bits[0] == 'meta':
                k = '_'.join(bits[1:])
                yield k, values
            else:
                yield key, values
        #
        elif values:
            process = METADATA_PROCESSORS[key]
            yield key, process(values, cfg)


class HtmlContent:

    def __init__(self, src, body, meta=None):
        self.src = src
        self.body = body
        self.meta = meta

    def __repr__(self):
        return self.src
    __str__ = __repr__

    def tojson(self):
        """Convert the content into a JSON dictionary
        """
        meta = self.meta or {}
        if self.src and 'modified' not in meta:
            meta['modified'] = modified_datetime(self.src)
        meta['body_length'] = len(self.body)
        meta['body'] = self.body
        return dict(_flatten(meta))


@register_reader
class HtmlReader:
    """Base class to read files.

    This class is used to process static files, and it can be inherited for
    other types of file. A Reader class must have the following attributes:

    - enabled: (boolean) tell if the Reader class is enabled. It
      generally depends on the import of some dependency.
    - file_extensions: a list of file extensions that the Reader will process.
    - extensions: a list of extensions to use in the reader (typical use is
      Markdown).

    """
    content = HtmlContent
    file_extensions = ['html']
    suffix = 'html'
    enabled = True
    extensions = None

    def __init__(self, app, ext=None):
        self.app = app
        self.ext = ext
        self.logger = app.logger
        self.config = app.config

    def __str__(self):
        return self.__class__.__name__

    def read(self, src, meta=None):
        """Read content from a file"""
        with open(src, 'rb') as text:
            body = text.read()
        return self.process(body.decode('utf-8'), src, meta=meta)

    def process(self, body, src=None, meta=None):
        """Return the dict containing document metadata
        """
        meta = dict(process_meta(meta, self.config)) if meta else {}
        meta['type'] = self.file_extensions[0]
        return self.content(src, body, meta)


@register_reader
class MarkdownReader(HtmlReader):
    """Reader for Markdown files"""
    enabled = bool(Markdown)
    file_extensions = ['markdown', 'mdown', 'mkd', 'md']
    suffix = 'html'

    @property
    def md(self):
        md = getattr(self.app, '_markdown', None)
        if md is None:
            extensions = list(self.config['MD_EXTENSIONS'])
            if 'meta' not in extensions:
                extensions.append('meta')
            self.app._markdown = Markdown(extensions=extensions)
        return self.app._markdown

    def process(self, raw, src=None, meta=None):
        raw = '%s\n\n%s' % (raw, self.links())
        md = self.md
        body = md.convert(raw)
        meta = tuple(chain_meta(meta, md.Meta))
        return super().process(body, src, meta=meta)

    def links(self):
        links = self.app.config.get('_MARKDOWN_LINKS_')
        if links is None:
            links = []
            for name, href in self.app.config['CONTENT_LINKS'].items():
                title = None
                if isinstance(href, dict):
                    title = href.get('title')
                    href = href['href']
                md = '[%s]: %s "%s"' % (name, href, title or name)
                links.append(md)
            links = '\n'.join(links)
            self.app.config['_MARKDOWN_LINKS_'] = links
        return links


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
