import os
import glob
import mimetypes

from pulsar.utils.httpurl import remove_double_slash

from lux import cached, get_reader
from lux.extensions import rest
from lux.extensions.rest import RestColumn
from lux.utils.files import get_rel_dir


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
    RestColumn('title')]


OPERATORS = {
    'eq': lambda x, y: x == y,
    'gt': lambda x, y: x > y,
    'ge': lambda x, y: x >= y,
    'lt': lambda x, y: x < y,
    'le': lambda x, y: x <= y
    }


class Content(rest.RestModel):
    '''A Rest model with file-system backend

    This model provide basic CRUD operations for a RestFul web API.
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

    def session(self, request):
        return Query(request, self)

    def query(self, request, session, *filters):
        return session

    def tojson(self, request, obj, exclude=None, **kw):
        data = obj.json(request)
        data['url'] = self.get_url(request, data['path'])
        data['html_url'] = self.get_html_url(request, data['path'])
        return data

    def get_target(self, request, **extra_data):
        '''Get a target for a form

        Used by HTML Router to get information about the LUX REST API
        of this Rest Model
        '''
        target = {'url': self.url}
        target.update(**extra_data)
        return target

    def exist(self, request, name):
        '''Check if a resource ``name`` exists
        '''
        try:
            self._content(request, name)
            return True
        except IOError:
            return False

    def read(self, request, name):
        '''Read content from file in the repository
        '''
        try:
            src, name, content = self._content(request, name)
            reader = get_reader(request.app, src)
            # path = self._path(request, name)
            return reader.process(content, name, src=src,
                                  meta=self.content_meta)
        except IOError:
            raise DataError('%s not available' % name)

    def all(self, request):
        '''Return list of all files stored in repo
        '''
        directory = self.directory
        files = glob.glob(os.path.join(directory, '*.%s' % self.ext))
        for file in files:
            filename = get_rel_dir(file, directory)
            yield self.read(request, filename).json(request)

    def serialise_model(self, request, data, in_list=False, **kw):
        if in_list:
            data.pop('html', None)
            data.pop('site', None)
        return data

    # INTERNALS
    def _content(self, request, name):
        '''Read content from file in the repository
        '''
        src = os.path.join(self.directory, name)
        if os.path.isdir(src):
            name = os.path.join(src, 'index')
        file_name = self._format_filename(name)
        src = os.path.join(self.directory, file_name)

        with open(src, 'rb') as f:
            content = f.read()

        ext = '.%s' % self.ext
        if name.endswith(ext):
            name = name[:-len(ext)]

        return src, name, content

    def _format_filename(self, filename):
        '''Append extension to file name
        '''
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            ext = '.%s' % self.ext
            if not filename.endswith(ext):
                filename = '%s%s' % (filename, ext)
        return filename

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
        return [d for d in self.model.all(request) if d['priority']]


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
