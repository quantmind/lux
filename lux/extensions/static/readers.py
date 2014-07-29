import json
import mimetypes

from dateutil.parser import parse

try:
    from markdown import Markdown
except ImportError:
    Markdown = False

from .contents import Processor, list_of
from .urlwrappers import Tag, Author, Category

READERS = {}

METADATA_PROCESSORS = dict(((p.name, p) for p in (
    Processor('name'),
    Processor('title'),
    Processor('slug'),
    Processor('description'),
    Processor('head-title'),
    Processor('head-description'),
    Processor('tag', list_of(Tag), multiple=True),
    Processor('date', lambda x, cfg: [parse(x)]),
    Processor('status'),
    Processor('image'),
    Processor('category', list_of(Category), multiple=True),
    Processor('author', list_of(Author), multiple=True),
    Processor('require_css', multiple=True),
    Processor('require_js', multiple=True),
    Processor('require_context', multiple=True),
    Processor('content_type', default='text/html'),
    Processor('draft', lambda x, cfg: json.loads(x)),
    Processor('template', default=lambda cfg: cfg['DEFAULT_TEMPLATE_ENGINE']),
    Processor('robots', default=['index', 'follow'], multiple=True),
    Processor('header-image'),
    Processor('twitter-image'),
    Processor('type')
)))


def register_reader(cls):
    for extension in cls.file_extensions:
        READERS[extension] = cls
    return cls


@register_reader
class BaseReader(object):
    """Base class to read files.

    This class is used to process static files, and it can be inherited for
    other t    pes of file. A Reader class must have the following attributes:

    - enabled: (boolean) tell if the Reader class is enabled. It
      generally depends on the import of some dependency.
    - file_extensions: a list of file extensions that the Reader will process.
    - extensions: a list of extensions to use in the reader (typical use is
      Markdown).

    """
    enabled = True
    file_extensions = [None, 'html', 'static']
    extensions = None

    def __init__(self, app):
        self.app = app
        self.logger = app.extensions['static'].logger
        self.config = app.config

    def __str__(self):
        return self.__class__.__name__

    def process_metadata(self, meta, src):
        """Return the dict containing document metadata
        """
        cfg = self.config
        output = dict(((p.name, p(cfg)) for p in METADATA_PROCESSORS.values()))
        for name, values in meta.items():
            name = name.lower()
            if name not in output:
                self.logger.warning("Unknown meta '%s' in '%s'", name, src)
            else:
                proc = METADATA_PROCESSORS[name].process
                for value in values:
                    try:
                        value = proc(value, cfg)
                    except Exception:
                        self.logger.exception("Could not process meta '%s' "
                                              "in '%s'", name, src)
                    output[name].extend(value)
        return output

    def read(self, source_path):
        '''Default read method
        '''
        ct, encoding = mimetypes.guess_type(source_path)
        if encoding or (ct and ct.startswith('text/')):
            with open(source_path, 'r', encoding=encoding or 'utf-8') as f:
                content = f.read()
        else:
            with open(source_path, 'rb') as f:
                content = f.read()
        metadata = {'content_type': ct,
                    'require_context': []}
        return content, metadata


@register_reader
class MarkdownReader(BaseReader):
    """Reader for Markdown files"""

    enabled = bool(Markdown)
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']

    def __init__(self, *args, **kwargs):
        super(MarkdownReader, self).__init__(*args, **kwargs)
        self.extensions = list(self.config['MD_EXTENSIONS'])
        if 'meta' not in self.extensions:
            self.extensions.append('meta')

    def read(self, source_path):
        """Parse content and metadata of markdown files"""

        self._md = md = Markdown(extensions=self.extensions)
        with open(source_path, encoding='utf-8') as text:
            raw = '%s\n\n%s' % (text.read(), self.links())
            content = md.convert(raw)
        metadata = self.process_metadata(self._md.Meta, source_path)
        return content, metadata

    def links(self):
        links = self.app.config.get('_MARKDOWN_LINKS_')
        if links is None:
            links = []
            for name, href in self.app.config['LINKS'].items():
                title = None
                if isinstance(href, dict):
                    title = href.get('title')
                    href = href['href']
                md = '[%s]: %s "%s"' % (name, href, title or name)
                links.append(md)
            links = '\n'.join(links)
            self.app.config['_MARKDOWN_LINKS_'] = links
        return links
