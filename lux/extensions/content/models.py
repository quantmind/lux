import os
import mimetypes

from pulsar import Http404
from pulsar.utils.httpurl import remove_double_slash
from pulsar.utils.slugify import slugify

from lux.core import cached, models
from lux.extensions.rest import RestModel, RestField
from lux.utils.data import as_tuple
from lux.utils.files import skipfile

from .contents import get_reader


FIELDS = [
    RestField('priority', sortable=True, type='int'),
    RestField('order', sortable=True, type='int'),
    RestField('slug', sortable=True),
    RestField('group', sortable=True),
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

    def tojson(self, request, instance, in_list=False, **kw):
        data = instance.obj
        if in_list:
            data.pop('body', None)
        return data

    def asset(self, filename):
        if self.html_url:
            path = '%s/%s' % (self.html_url, filename)
        else:
            path = filename
        src = os.path.join(self.directory, filename)
        return dict(src=src, path=path)

    # INTERNALS
    def _path(self, request, path):
        '''relative pathof content
        '''
        return remove_double_slash('/%s/%s' % (self.url, path))

    def content(self, data):
        body = data['body']
        return body


class QuerySession(models.Query):
    _filtered_data = None
    _data = None
    _limit = None
    _offset = None
    _paths = None

    def __init__(self, model, request):
        super().__init__(model)
        self._filters = []
        self._groups = []
        self._sortby = []
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
        data = self.all()
        if data:
            if len(data) > 1:
                self.request.logger.error('Multiple result found for model %s.'
                                          'returning the first' % self.name)
            return data[0]
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
        self._filtered_data = None
        self._paths = args

    def filter_field(self, field, op, value):
        self._filtered_data = None
        if op in OPERATORS:
            op = OPERATORS[op]
            if field == 'group':
                self._groups.extend(as_tuple(value))
            self._filters.append((field, op, value))
        else:
            self.app.logger.error('Could not apply filter %s to %s',
                                  op, self)

    def sortby_field(self, field, direction):
        self._sortby.append((field, direction))

    def all(self):
        data = self._get_data()
        for field, direction in self._sortby:
            if direction == 'desc':
                data = [desc(d, field) for d in data]
            else:
                data = [asc(d, field) for d in data]
            data = [s.d for s in sorted(data)]
        if self._offset:
            data = data[self._offset:]
        if self._limit:
            data = data[:self._limit]
        return data

    #  INTERNALS
    def _get_data(self):
        model = self.model
        if self._filtered_data is None:
            if self._data is None:
                self._data = []
                for group in self._groups:
                    cache = cached(app=self.app, key='contents:%s' % group)
                    self._data.extend(cache(self._all)(group))
            self._filtered_data = data = []
            for content in self._data:
                if self._filter(content):
                    data.append(model.instance(content, self.fields))
        return self._filtered_data

    def _sort(self, c):
        if self._sort_field in c:
            return

    def _filter(self, content):
        for field, op, value in self._filters:
            val = content.get(field)
            try:
                if not op(val, value):
                    return False
            except Exception:
                return False
        return True

    def _all(self, group):
        """Contents in this model group
        """
        model = self.model
        directory = os.path.join(model.directory, group)
        ext = '.%s' % model.ext
        reader = get_reader(self.app, ext)
        data = []
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                if skipfile(filename):
                    continue

                if dirpath != directory:
                    path = os.path.relpath(dirpath, directory)
                    filename = os.path.join(path, filename)

                if filename.endswith(ext):
                    slug = filename[:-len(ext)]
                    src = os.path.join(directory, filename)
                    meta = dict(path='/%s/%s' % (group, slug),
                                group=group,
                                slug=slug)
                    data.append(reader.read(src, meta).tojson())
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
