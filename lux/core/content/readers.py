from itertools import chain

from pulsar.utils.slugify import slugify

from .contents import (ContentFile, HtmlContentFile, METADATA_PROCESSORS,
                       HtmlFile, register_reader)
from .urlwrappers import MultiValue

try:
    from markdown import Markdown
except ImportError:     # pragma    nocover
    Markdown = False

Restructured = False


def guess(value):
    return value if len(value) > 1 else value[-1]


DEFAULTS = (('priority', 1),
            ('order', 0))


@register_reader
class BaseReader(object):
    """Base class to read files.

    This class is used to process static files, and it can be inherited for
    other types of file. A Reader class must have the following attributes:

    - enabled: (boolean) tell if the Reader class is enabled. It
      generally depends on the import of some dependency.
    - file_extensions: a list of file extensions that the Reader will process.
    - extensions: a list of extensions to use in the reader (typical use is
      Markdown).

    """
    enabled = True
    file_extensions = ['']
    extensions = None
    content = ContentFile

    def __init__(self, app, ext=None):
        self.app = app
        self.ext = ext
        self.logger = app.logger
        self.config = app.config

    def __str__(self):
        return self.__class__.__name__

    def read(self, src):
        """Parse content and metadata of markdown files"""
        with open(src, 'r') as text:
            body = text.read()
        return self.process(body, src)

    def process(self, body, src, meta=None):
        """Return the dict containing document metadata
        """
        if meta is None:
            meta = {}
        cfg = self.config
        head_meta = {}
        meta = meta.items() if meta else ()
        meta_input = chain(DEFAULTS, meta)
        meta = {}
        as_list = MultiValue()
        for key, values in meta_input:
            key = slugify(key, separator='_')
            if not isinstance(values, (list, tuple)):
                values = (values,)
            if key not in METADATA_PROCESSORS:
                bits = key.split('_', 1)
                if len(bits) > 1:
                    k = ':'.join(bits[1:])
                    if bits[0] == 'meta':
                        meta[k] = guess(as_list(values, cfg))
                        continue
                    if bits[0] == 'head':
                        head_meta[k] = guess(as_list(values, cfg))
                        continue
                    if bits[0] == 'og' or bits[0] == 'twitter':
                        k = ':'.join(bits)
                        head_meta[k] = guess(as_list(values, cfg))
                        continue
                self.logger.warning("Unknown meta '%s' in '%s'", key, src)
            #
            elif values:
                # Remove default values if any
                proc = METADATA_PROCESSORS[key]
                meta[key] = proc(values, cfg)
        if meta.get('priority') == '0':
            head_meta['robots'] = ['noindex', 'nofollow']
        meta['head'] = head_meta
        return body, meta


@register_reader
class HtmlReader(BaseReader):
    content = HtmlFile
    file_extensions = ['html']


@register_reader
class MarkdownReader(BaseReader):
    """Reader for Markdown files"""
    enabled = bool(Markdown)
    content = HtmlContentFile
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']

    @property
    def md(self):
        md = getattr(self.app, '_markdown', None)
        if md is None:
            extensions = list(self.config['MD_EXTENSIONS'])
            if 'meta' not in extensions:
                extensions.append('meta')
            self.app._markdown = Markdown(extensions=extensions)
        return self.app._markdown

    def process(self, raw, src, meta=None):
        raw = '%s\n\n%s' % (raw, self.links())
        md = self.md
        body = md.convert(raw)
        meta = meta if meta is not None else {}
        meta.update(md.Meta)
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


@register_reader
class RestructuredReader(BaseReader):
    enabled = bool(Restructured)
    content = HtmlContentFile
    file_extensions = ['rst']

    def process(self, raw, path, **params):
        raw = raw.decode('utf-8')
        re = Restructured(raw)
        body = re.convert()
        return self.post_process(body, re.Meta, path, **params)
