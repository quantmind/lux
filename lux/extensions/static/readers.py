import datetime
import logging
import os
import re

try:
    from markdown import Markdown
except ImportError:
    Markdown = False

from .contents import Page, Category, Tag, Author


READERS = {}
METADATA_PROCESSORS = {
    'tags': lambda x, y: [Tag(tag, y) for tag in x.split(',')],
    'date': lambda x, y: get_date(x),
    'modified': lambda x, y: get_date(x),
    'status': lambda x, y: x.strip(),
    'category': Category,
    'author': Author,
    'authors': lambda x, y: [Author(author, y) for author in x],
}


def process_file(app, path):
    if not os.path.isfile(path):
        path = '%s.%s' % (path, app.config['SOURCE_SUFFIX'])
    if not os.path.isfile(path):
        app.logger.warning('Could not locate %s', path)
        return
    extension = path.split('.')[-1]
    Reader = READERS.get(extension)
    if not Reader:
        app.logger.warning('Reader for %s extension not available', extension)
    elif not Reader.enabled:
        app.logger.warning('Missing dependencies for %s' % Reader.__name__)
    else:
        reader = Reader(app)
        return reader.read(path)


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
        with open(source_path) as text:
            content = self._md.convert(text.read())
        metadata = self._parse_metadata(self._md.Meta)
        return content, metadata


class Readers(object):

    def __init__(self, settings=None):
        self.settings = settings or {}
        self.readers = {}
        self.reader_classes = {}

        for cls in [BaseReader] + BaseReader.__subclasses__():
            if not cls.enabled:
                if self.__class__.warn_missing_deps:
                    logger.debug('Missing dependencies for {}'
                                 .format(', '.join(cls.file_extensions)))
                continue

            for ext in cls.file_extensions:
                self.reader_classes[ext] = cls

        self.__class__.warn_missing_deps = False

        if self.settings['READERS']:
            self.reader_classes.update(self.settings['READERS'])

        signals.readers_init.send(self)

        for fmt, reader_class in self.reader_classes.items():
            if not reader_class:
                continue

            self.readers[fmt] = reader_class(self.settings)

    @property
    def extensions(self):
        return self.readers.keys()

    def read_file(self, base_path, path, content_class=Page, fmt=None,
                  context=None, preread_signal=None, preread_sender=None,
                  context_signal=None, context_sender=None):
        """Return a content object parsed with the given format."""

        path = os.path.abspath(os.path.join(base_path, path))
        source_path = os.path.relpath(path, base_path)
        logger.debug('read file {} -> {}'.format(
            source_path, content_class.__name__))

        if not fmt:
            _, ext = os.path.splitext(os.path.basename(path))
            fmt = ext[1:]

        if fmt not in self.readers:
            raise TypeError(
                'Pelican does not know how to parse {}'.format(path))

        if preread_signal:
            logger.debug('signal {}.send({})'.format(
                preread_signal, preread_sender))
            preread_signal.send(preread_sender)

        reader = self.readers[fmt]

        metadata = default_metadata(
            settings=self.settings, process=reader.process_metadata)
        metadata.update(path_metadata(
            full_path=path, source_path=source_path,
            settings=self.settings))
        metadata.update(parse_path_metadata(
            source_path=source_path, settings=self.settings,
            process=reader.process_metadata))

        content, reader_metadata = reader.read(path)
        metadata.update(reader_metadata)

        # eventually filter the content with typogrify if asked so
        if content and self.settings['TYPOGRIFY']:
            from typogrify.filters import typogrify
            content = typogrify(content)
            metadata['title'] = typogrify(metadata['title'])

        if context_signal:
            logger.debug('signal {}.send({}, <metadata>)'.format(
                context_signal, context_sender))
            context_signal.send(context_sender, metadata=metadata)

        return content_class(content=content, metadata=metadata,
                             settings=self.settings, source_path=path,
                             context=context)



def default_metadata(settings=None, process=None):
    metadata = {}
    if settings:
        if 'DEFAULT_CATEGORY' in settings:
            value = settings['DEFAULT_CATEGORY']
            if process:
                value = process('category', value)
            metadata['category'] = value
        if settings.get('DEFAULT_DATE', None) and settings['DEFAULT_DATE'] != 'fs':
            metadata['date'] = datetime.datetime(*settings['DEFAULT_DATE'])
    return metadata


def path_metadata(full_path, source_path, settings=None):
    metadata = {}
    if settings:
        if settings.get('DEFAULT_DATE', None) == 'fs':
            metadata['date'] = datetime.datetime.fromtimestamp(
                os.stat(full_path).st_ctime)
        metadata.update(settings.get('EXTRA_PATH_METADATA', {}).get(
            source_path, {}))
    return metadata


def parse_path_metadata(source_path, settings=None, process=None):
    """Extract a metadata dictionary from a file's path

    >>> import pprint
    >>> settings = {
    ...     'FILENAME_METADATA': '(?P<slug>[^.]*).*',
    ...     'PATH_METADATA':
    ...         '(?P<category>[^/]*)/(?P<date>\d{4}-\d{2}-\d{2})/.*',
    ...     }
    >>> reader = BaseReader(settings=settings)
    >>> metadata = parse_path_metadata(
    ...     source_path='my-cat/2013-01-01/my-slug.html',
    ...     settings=settings,
    ...     process=reader.process_metadata)
    >>> pprint.pprint(metadata)  # doctest: +ELLIPSIS
    {'category': <pelican.urlwrappers.Category object at ...>,
     'date': datetime.datetime(2013, 1, 1, 0, 0),
     'slug': 'my-slug'}
    """
    metadata = {}
    dirname, basename = os.path.split(source_path)
    base, ext = os.path.splitext(basename)
    subdir = os.path.basename(dirname)
    if settings:
        checks = []
        for key, data in [('FILENAME_METADATA', base),
                          ('PATH_METADATA', source_path)]:
            checks.append((settings.get(key, None), data))
        if settings.get('USE_FOLDER_AS_CATEGORY', None):
            checks.insert(0, ('(?P<category>.*)', subdir))
        for regexp, data in checks:
            if regexp and data:
                match = re.match(regexp, data)
                if match:
                    # .items() for py3k compat.
                    for k, v in match.groupdict().items():
                        if k not in metadata:
                            k = k.lower()  # metadata must be lowercase
                            if process:
                                v = process(k, v)
                            metadata[k] = v
    return metadata
