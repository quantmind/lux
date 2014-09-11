import os
import imp
import mimetypes
from itertools import chain

try:
    from markdown import Markdown
except ImportError:
    Markdown = False

from pulsar.apps.wsgi import AsyncString

from .contents import (Snippet, METADATA_PROCESSORS, slugify, is_text,
                       SkipBuild)
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
        meta = dict(((p.name, p(cfg)) for p in METADATA_PROCESSORS.values()))
        for key, values in meta_input:
            key = slugify(key, separator='_')
            if not isinstance(values, (list, tuple)):
                values = (values,)
            if key not in meta:
                bits = key.split('_', 1)
                if len(bits) > 1:
                    k = ':'.join(bits[1:])
                    if bits[0] == 'context':
                        context[k] = data = []
                        for value in values:
                            data.extend(as_list(value, cfg))
                        continue
                    if bits[0] == 'meta':
                        data = []
                        for value in values:
                            data.extend(as_list(value, cfg))
                        meta[k] = guess(data)
                        continue
                    if bits[0] == 'head':
                        data = []
                        for value in values:
                            data.extend(as_list(value, cfg))
                        head_meta[k] = guess(data).value()
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
        if meta['priority'].value() == '0':
            content = content.as_draft()
            meta['robots'].clear()
            meta['robots'].extend(['noindex', 'nofollow'])
        content = content or Snippet
        meta['head'] = head_meta
        return content(body, meta, src, name, context, **params)

    def read(self, source_path, name, **params):
        '''Default read method
        '''
        ct, encoding = mimetypes.guess_type(source_path)
        if is_text(ct):
            with open(source_path, 'r', encoding=encoding or 'utf-8') as f:
                body = f.read()
        else:
            ct = ct or 'application/octet-stream'
            with open(source_path, 'rb') as f:
                body = f.read()
            if self.ext and not name.endswith('.%s' % self.ext):
                name = '%s.%s' % (name, self.ext)
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
