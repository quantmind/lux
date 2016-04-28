from .contents import ContentFile, HtmlContent, register_reader, process_meta
from .utils import chain_meta

try:
    from markdown import Markdown
except ImportError:     # pragma    nocover
    Markdown = False

Restructured = False


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
    suffix = None
    content = ContentFile

    def __init__(self, app, ext=None):
        self.app = app
        self.ext = ext
        self.logger = app.logger
        self.config = app.config

    def __str__(self):
        return self.__class__.__name__

    def read(self, src, meta=None):
        """Parse content and metadata of markdown files"""
        with open(src, 'rb') as text:
            body = text.read()
        return self.process(body.decode('utf-8'), src, meta=meta)

    def process(self, body, src, meta=None):
        """Return the dict containing document metadata
        """
        meta = dict(process_meta(meta, self.config)) if meta else None
        return self.content(src, body, meta)


@register_reader
class HtmlReader(BaseReader):
    content = HtmlContent
    file_extensions = ['html']
    suffix = 'html'


@register_reader
class MarkdownReader(BaseReader):
    """Reader for Markdown files"""
    enabled = bool(Markdown)
    content = HtmlContent
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']
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

    def process(self, raw, src, meta=None):
        raw = '%s\n\n%s' % (raw, self.links())
        md = self.md
        body = md.convert(raw)
        return super().process(body, src, meta=chain_meta(meta, md.Meta))

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
    content = HtmlContent
    file_extensions = ['rst']
    suffix = 'html'

    def process(self, raw, src, meta=None):
        re = Restructured(raw)
        body = re.convert()
        return super().process(body, src, meta=chain_meta(meta, re.Meta))
