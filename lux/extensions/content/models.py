import os
import mimetypes

from pulsar.utils.httpurl import remove_double_slash
from pulsar.utils.slugify import slugify

from lux.core import cached
from lux.core.content import get_reader, ContentFile
from lux.extensions import rest
from lux.extensions.rest import RestColumn
from lux.utils.files import skipfile


__all__ = ('_b', 'DataError', 'Content')


def _b(value):
    '''Return string literals
    '''
    return value.encode('utf-8')


class DataError(Exception):
    pass


COLUMNS = [
    RestColumn('priority', sortable=True, type='int'),
    RestColumn('order', sortable=True, type='int'),
    RestColumn('slug', sortable=True),
    RestColumn('path', sortable=True),
    RestColumn('title')]


OPERATORS = {
    'eq': lambda x, y: x == y,
    'ne': lambda x, y: x != y,
    'gt': lambda x, y: x > y,
    'ge': lambda x, y: x >= y,
    'lt': lambda x, y: x < y,
    'le': lambda x, y: x <= y
    }


snippets_url = 'snippets'


class Snippet(rest.RestModel):
    pass


class Content(rest.RestModel):
    '''A Content model with file-system backend

    This model provide read-only operations
    '''
    def __init__(self, name, repo, path=None, ext='md', content_meta=None,
                 columns=None, api_prefix='content'):
        directory = os.path.join(repo, name)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        self.directory = directory
        self.ext = ext
        self.content_meta = content_meta or {}
        if path is None:
            path = name
        columns = columns or COLUMNS[:]
        api_url = '%s/%s' % (api_prefix, name)
        super().__init__(name, columns=columns, url=api_url, html_url=path)

    def get_instance(self, request, path):
        return self.serialise_model(request, self.read(request, path))

    def session(self, request):
        return Query(request, self)

    def query(self, request, session, *filters):
        if filters:
            request.logger.warning('Cannot use positional filters in %s',
                                   request.path)
        return session

    def serialise_model(self, request, content, in_list=False, **kw):
        if isinstance(content, ContentFile):
            return content.response(request)
        if not isinstance(content, dict):
            content = self.tojson(request, content, **kw)
        if in_list:
            content.pop('body', None)
        return content

    def tojson(self, request, obj, exclude=None, **kw):
        meta = obj.json(request.app)
        path = meta.get('path')
        if path is not None:
            meta['slug'] = slugify(path) or 'index'
            if self.html_url:
                path = '/'.join(path.split('/')[2:])
            meta['url'] = self.get_url(request, path)
            meta['html_url'] = self.get_html_url(request, path)
        return meta

    def get_target(self, request, **extra_data):
        '''Get a target for a form

        Used by HTML Router to get information about the LUX REST API
        of this Rest Model
        '''
        target = {'url': self.url}
        target.update(**extra_data)
        return target

    def read(self, request, path):
        '''Read content from file in the repository
        '''
        src = os.path.join(self.directory, path)
        if os.path.isdir(src):
            src = os.path.join(src, 'index')

        if src.endswith('.html'):
            raise DataError

        # Handle files which are not html
        content_type, _ = mimetypes.guess_type(src)
        if content_type and os.path.isfile(src):
            return ContentFile(src, content_type=content_type)

        # Add extension
        ext = '.%s' % self.ext
        src = '%s%s' % (src, ext)
        if not os.path.isfile(src):
            raise DataError

        path = os.path.relpath(src, self.directory)
        #
        # Add html_url if available
        if self.html_url:
            path = '%s/%s' % (self.html_url, path)
        #
        # Remove extension
        path = path[:-len(ext)]
        if path.endswith('index'):
            path = path[:-5]
        if path.endswith('/'):
            path = path[:-1]
        path = '/%s' % path
        meta = self.content_meta.copy()
        meta['path'] = path
        return get_reader(request.app, src).read(src, meta)

    def asset(self, filename):
        if self.html_url:
            path = '%s/%s' % (self.html_url, filename)
        else:
            path = filename
        src = os.path.join(self.directory, filename)
        return dict(src=src, path=path)

    def all(self, request, force=False):
        """Generator of contents in this model

        :param force: if true all content is yielded, otherwise only content
            matching the extension
        """
        directory = self.directory
        ext = '.%s' % self.ext
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                if skipfile(filename):
                    continue
                if dirpath != directory:
                    path = os.path.relpath(dirpath, directory)
                    filename = os.path.join(path, filename)

                if not filename.endswith(ext):
                    if force:
                        yield self.asset(filename)
                else:
                    filename = filename[:-len(ext)]
                    yield self.read(request, filename)

    # INTERNALS
    def _path(self, request, path):
        '''relative pathof content
        '''
        return remove_double_slash('/%s/%s' % (self.url, path))

    def content(self, data):
        body = data['body']
        return body

    def _do_sortby(self, request, query, field, direction):
        return query.sortby(field, direction)

    def _do_filter(self, request, query, field, op, value):
        return query.filter(field, op, value)


class Query:
    _data = None
    _limit = None
    _offset = None

    def __init__(self, request, model):
        self.request = request
        self.model = model

    def __enter__(self):
        return self

    def __repr__(self):
        if self._data is None:
            return self.__class__.__name__
        else:
            return repr(self._data)
    __str__ = __repr__

    def __exit__(self, type, value, traceback):
        pass

    def limit(self, v):
        self._limit = v
        return self

    def offset(self, v):
        self._offset = v
        return self

    def count(self):
        return len(self._get_data())

    def sortby(self, field, direction):
        data = self._get_data()
        if direction == 'desc':
            data = [desc(d, field) for d in data]
        else:
            data = [asc(d, field) for d in data]
        self._data = [s.d for s in sorted(data)]
        return self

    def filter(self, field, op, value):
        data = []
        op = OPERATORS.get(op)
        if op:
            for content in self._get_data():
                val = content.get(field)
                try:
                    if op(val, value):
                        data.append(content)
                except Exception:
                    pass
        self._data = data
        return self

    def all(self):
        data = self._get_data()
        if self._offset:
            data = data[self._offset:]
        if self._limit:
            data = data[:self._limit]
        return data

    #  INTERNALS
    def _get_data(self):
        if self._data is None:
            self._data = self.read_files(self.request)
        return self._data

    def _sort(self, c):
        if self._sort_field in c:
            return

    @cached
    def read_files(self, request):
        data = []
        instances = self.model.all(request)
        for d in self.model.serialise(request, instances):
            if d.get('priority', 1):
                data.append(d)
        return data


class asc:
    __slots__ = ('d', 'value')

    def __init__(self, d, field):
        self.d = d
        self.value = d.get(field)

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        if self.value is None:
            return False
        elif other.value is None:
            return True
        else:
            return self.value < other.value

    def __gt__(self, other):
        if other.value is None:
            return False
        elif self.value is None:
            return True
        else:
            return self.value > other.value


class desc(asc):

    def __gt__(self, other):
        if self.value is None:
            return False
        elif other.value is None:
            return True
        else:
            return self.value < other.value

    def __lt__(self, other):
        if self.value is None:
            return False
        elif other.value is None:
            return True
        else:
            return self.value > other.value
