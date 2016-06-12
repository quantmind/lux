import os
import mimetypes

from pulsar import Http404
from pulsar.utils.httpurl import remove_double_slash
from pulsar.utils.slugify import slugify

from lux.core import cached, models
from lux.extensions.rest import RestModel, RestField
from lux.utils.files import skipfile

from .contents import get_reader


FIELDS = [
    RestField('priority', sortable=True, type='int'),
    RestField('order', sortable=True, type='int'),
    RestField('slug', sortable=True),
    RestField('path', sortable=True),
    RestField('title')]


OPERATORS = {
    'eq': lambda x, y: x == y,
    'ne': lambda x, y: x != y,
    'gt': lambda x, y: x > y,
    'ge': lambda x, y: x >= y,
    'lt': lambda x, y: x < y,
    'le': lambda x, y: x <= y
}


class ContentModel(RestModel):
    '''A Content model with file-system backend

    This model provide read-only operations
    '''
    def __init__(self, location, name='content', fields=None, ext='md', **kw):
        if not os.path.isdir(location):
            os.makedirs(location)
        self.directory = location
        self.ext = ext
        fields = fields or FIELDS[:]
        kw['id_field'] = 'path'
        super().__init__(name, fields=fields, **kw)

    def session(self, request, session=None):
        return QuerySession(self, request)

    def get_query(self, session):
        return session

    def tojson(self, request, content, in_list=False, **kw):
        content = content.json(request.app)
        path = content.get('path')
        if path is not None:
            content['slug'] = slugify(path) or 'index'
        if in_list:
            content.pop('body', None)
        return content

    def asset(self, filename):
        if self.html_url:
            path = '%s/%s' % (self.html_url, filename)
        else:
            path = filename
        src = os.path.join(self.directory, filename)
        return dict(src=src, path=path)

    @cached
    def all(self, request):
        """Generator of contents in this model

        :param force: if true all content is yielded, otherwise only content
            matching the extension
        """
        group = request.urlargs.get('group')
        if not group:
            return []
        directory = os.path.join(self.directory, group)
        ext = '.%s' % self.ext
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                if skipfile(filename):
                    continue

                path = os.path.relpath(dirpath, self.directory)
                filename = os.path.join(path, filename)

                if filename.endswith(ext):
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


class QuerySession(models.Query):
    _data = None
    _limit = None
    _offset = None
    _paths = None

    def __init__(self, model, request):
        super().__init__(model)
        self.request = request

    def __repr__(self):
        if self._data is None:
            return self.__class__.__name__
        else:
            return repr(self._data)
    __str__ = __repr__

    # Session methods
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def add(self, instance):
        pass

    def flush(self):
        pass

    # Query methods
    def one(self):
        if self._paths:
            return self.read(self._paths[0])
        else:
            raise Http404

    def limit(self, v):
        self._limit = v
        return self

    def offset(self, v):
        self._offset = v
        return self

    def count(self):
        return len(self._get_data())

    def filter_args(self, args):
        self._paths = args

    def sortby_field(self, field, direction):
        data = self._get_data()
        if direction == 'desc':
            data = [desc(d, field) for d in data]
        else:
            data = [asc(d, field) for d in data]
        self._data = [s.d for s in sorted(data)]
        return self

    def filter_field(self, field, op, value):
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
        data = self.self.model.all(self.request)
        if self._offset:
            data = data[self._offset:]
        if self._limit:
            data = data[:self._limit]
        return data

    #  INTERNALS
    def _sort(self, c):
        if self._sort_field in c:
            return

    def read(self, path):
        '''Read content from file in the repository
        '''
        model = self.model
        src = os.path.join(model.directory, path)
        if os.path.isdir(src):
            src = os.path.join(src, 'index')

        # Don't serve path with a suffix
        content_type, _ = mimetypes.guess_type(src)
        if content_type:
            raise Http404

        # Add extension
        ext = '.%s' % model.ext
        src = '%s%s' % (src, ext)
        if not os.path.isfile(src):
            raise Http404

        path = os.path.relpath(src, model.directory)
        #
        # Remove extension
        path = path[:-len(ext)]
        if path.endswith('index'):
            path = path[:-5]
        if path.endswith('/'):
            path = path[:-1]
        path = '/%s' % path
        meta = dict(path=path)
        return get_reader(self.app, src).read(src, meta)


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
