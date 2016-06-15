import os

from pulsar.utils.httpurl import remove_double_slash

from lux.core import cached
from lux.extensions.rest import RestModel, RestField, Query
from lux.utils.files import skipfile

from .contents import get_reader


FIELDS = [
    RestField('priority', sortable=True, type='int'),
    RestField('order', sortable=True, type='int'),
    RestField('slug', sortable=True),
    RestField('group', sortable=True),
    RestField('title')
]


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
        kw['id_field'] = 'slug'
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


class Session:

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def add(self, instance):
        pass

    def delete(self, instance):
        pass

    def flush(self):
        pass


class QuerySession(Query, Session):

    def __init__(self, model, request):
        super().__init__(model, request)
        self._groups = []

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
