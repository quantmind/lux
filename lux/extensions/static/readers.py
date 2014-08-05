import json
import mimetypes

try:
    from markdown import Markdown
except ImportError:
    Markdown = False

from .contents import Draft, Snippet, METADATA_PROCESSORS, slugify
from .urlwrappers import guess, as_list


READERS = {}


def register_reader(cls):
    for extension in cls.file_extensions:
        READERS[extension] = cls
    return cls


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
    file_extensions = []
    extensions = None

    def __init__(self, app):
        self.app = app
        self.logger = app.extensions['static'].logger
        self.config = app.config

    def __str__(self):
        return self.__class__.__name__

    def process(self, body, meta_input, src, name, content=None, **params):
        """Return the dict containing document metadata
        """
        cfg = self.config
        context = {}
        meta = dict(((p.name, p(cfg)) for p in METADATA_PROCESSORS.values()))
        for key, values in meta_input.items():
            key = key.lower()
            if key not in meta:
                key = slugify(key, separator='_')
                bits = key.split('_', 1)
                if len(bits) == 2:
                    if bits[0] == 'context':
                        context[bits[1]] = data = []
                        for value in values:
                            data.extend(as_list(value, cfg))
                        continue
                    if bits[0] == 'meta':
                        data = []
                        for value in values:
                            data.extend(as_list(value, cfg))
                        meta[bits[1]] = guess(data)
                        continue
                self.logger.warning("Unknown meta '%s' in '%s'", key, src)
            #
            elif values:
                # Remove default values if any
                proc = METADATA_PROCESSORS[key].process
                meta[key].clear()
                for value in values:
                    try:
                        value = proc(value, cfg)
                    except Exception:
                        self.logger.exception("Could not process meta '%s' "
                                              "in '%s'", key, src)
                    meta[key].extend(value)
        if meta['draft'].value():
            content = Draft
        content = content or Snippet
        return content(body, meta, src, name, context, **params)

    def read(self, source_path, name, **params):
        '''Default read method
        '''
        ct, encoding = mimetypes.guess_type(source_path)
        if encoding or (ct and ct.startswith('text/')):
            ct = ct or 'text/plain'
            with open(source_path, 'r', encoding=encoding or 'utf-8') as f:
                body = f.read()
        else:
            ct = ct or 'application/octet-stream'
            with open(source_path, 'rb') as f:
                body = f.read()
        metadata = {'content_type': [ct]}
        return self.process(body, metadata, source_path, name, **params)


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

    def read(self, source_path, name, **params):
        """Parse content and metadata of markdown files"""
        self._md = md = Markdown(extensions=self.extensions)
        with open(source_path, encoding='utf-8') as text:
            raw = '%s\n\n%s' % (text.read(), self.links())
            body = md.convert(raw)
        return self.process(body, self._md.Meta, source_path, name, **params)

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
