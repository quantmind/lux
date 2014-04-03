import codecs
import datetime
import logging
import os
import re
import json

from dateutil.parser import parse

try:
    from markdown import Markdown
except ImportError:
    Markdown = False

from .contents import Page, Category, Tag, Author


READERS = {}
METADATA_PROCESSORS = {
    'tags': lambda x, y: [Tag(tag, y) for tag in x.split(',')],
    'date': lambda x, y: parse(x),
    'modified': lambda x, y: parse(x),
    'status': lambda x, y: x.strip(),
    'category': Category,
    'author': Author,
    'authors': lambda x, y: [Author(author, y) for author in x],
    'requires': lambda x, y: [script.strip() for script in x.split(',')],
    'draft': lambda x, y: json.loads(x)
}


def get_rel_dir(d, base, res=''):
    if d == base:
        return res
    br, r = os.path.split(d)
    if res:
        r = os.path.join(r, res)
    return get_rel_dir(br, base, r)


def register_reader(cls):
    for extension in cls.file_extensions:
        READERS[extension] = cls
    return cls


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
    file_extensions = ['static']
    extensions = None

    def __init__(self, app):
        self.app = app
        self.config = app.config

    def __str__(self):
        return self.__class__.__name__

    def process_metadata(self, name, value):
        if name in METADATA_PROCESSORS:
            return METADATA_PROCESSORS[name](value, self.config)
        return value

    def read(self, source_path):
        "No-op parser"
        content = None
        metadata = {}
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

    def _parse_metadata(self, meta):
        """Return the dict containing document metadata"""
        output = {}
        for name, value in meta.items():
            name = name.lower()
            if name == "summary":
                summary_values = "\n".join(value)
                # reset the markdown instance to clear any state
                self._md.reset()
                summary = self._md.convert(summary_values)
                output[name] = self.process_metadata(name, summary)
            else:
                output[name] = self.process_metadata(name, value[0])
        return output

    def read(self, source_path):
        """Parse content and metadata of markdown files"""

        self._md = Markdown(extensions=self.extensions)
        with codecs.open(source_path, encoding='utf-8') as text:
            content = self._md.convert(text.read())
        metadata = self._parse_metadata(self._md.Meta)
        return content, metadata

