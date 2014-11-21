import os
import imp
import mimetypes
from itertools import chain

try:
    from markdown import Markdown
except ImportError:
    Markdown = False

Restructured = False

from pulsar.apps.wsgi import AsyncString

from .contents import (Content, METADATA_PROCESSORS, slugify, is_html,
                       SkipBuild)
from .urlwrappers import MultiValue


READERS = {}


def register_reader(cls):
    for extension in cls.file_extensions:
        READERS[extension] = cls
    return cls


def guess(value):
    return value if len(value) > 1 else value[-1]


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
    file_extensions = []
    extensions = None
    content = Content

    def __init__(self, app, ext=None):
        self.app = app
        self.ext = ext
        self.logger = app.extensions['static'].logger
        self.config = app.config

    def __str__(self):
        return self.__class__.__name__

    def process(self, body, meta_input, src, name, content=None, meta=None,
                **params):
        """Return the dict containing document metadata
        """
        cfg = self.config
        context = {}
        head_meta = {}
        meta_input = meta_input.items()
        if meta:
            meta_input = chain(meta.items(), meta_input)
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
                    if bits[0] == 'context':
                        context[k] = as_list(values, cfg)
                        continue
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
        content = content or self.content
        if meta.get('priority') == '0':
            content = content.as_draft()
            meta['robots'] = ['noindex', 'nofollow']
        meta['head'] = head_meta
        if params:
            pass
        return content(self.app, body, meta, src, name, context, **params)

    def read(self, source_path, name, **params):
        '''Default read method
        '''
        ct, encoding = mimetypes.guess_type(source_path)
        with open(source_path, 'rb') as f:
            body = f.read()
        if is_html(ct):
            body = body.decode(encoding=encoding or 'utf-8')
        else:
            ct = ct or 'application/octet-stream'
            if self.ext and not name.endswith('.%s' % self.ext):
                name = '%s.%s' % (name, self.ext)
        metadata = {'content_type': ct}
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
        with open(source_path, 'rb') as text:
            raw = text.read().decode('utf-8')
        raw = '%s\n\n%s' % (raw, self.links())
        body = md.convert(raw)
        meta = self._md.Meta
        meta['content_type'] = 'text/html'
        return self.process(body, meta, source_path, name, **params)

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


@register_reader
class PythonReader(BaseReader):
    '''Reader for Python template generator files
    '''
    file_extensions = ['py']

    def read(self, source_path, name, **params):
        name = os.path.basename(source_path).split('.')[0]
        mod = imp.load_source(name, source_path)
        if not hasattr(mod, 'template'):
            raise SkipBuild
        content = mod.template()
        if isinstance(content, AsyncString):
            ct = content._content_type
            content = content.render()
        else:
            ct = 'text/plain'
        metadata = {'content_type': [ct]}
        return self.process(content, metadata, source_path, name, **params)


@register_reader
class RestructuredReader(BaseReader):
    enabled = bool(Restructured)
    file_extensions = ['rst']

    def read(self, source_path, name, **params):
        with open(source_path, encoding='utf-8') as text:
            raw = text.read()
            re = Restructured(raw)
        body = re.convert()
        return self.process(body, re.Meta, source_path, name, **params)
