import os
import glob
import mimetypes

from dulwich.porcelain import rm, add, init, commit, open_repo
from dulwich.file import GitFile
from dulwich.errors import NotGitRepository

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
    '''A Rest model with git backend using dulwich_

    This model provide basic CRUD operations for a RestFul web API.

    .. _dulwich: https://www.samba.org/~jelmer/dulwich/docs/
    '''
    def __init__(self, name, repo, path=None, ext='md', content_meta=None,
                 columns=None, **kwargs):
        try:
            self.repo = open_repo(repo)
        except NotGitRepository:
            self.repo = init(repo)
        self.path = repo
        self.ext = ext
        self.content_meta = content_meta or {}
        if path is None:
            path = name
        if path:
            self.path = os.path.join(self.path, path)
        self.path = self.path
        columns = columns or COLUMNS[:]
        super().__init__(name, columns=columns, **kwargs)

    def session(self, request):
        return Query(request, self)

    def get_target(self, request, **extra_data):
        '''Get a target for a form

        Used by HTML Router to get information about the LUX REST API
        of this Rest Model
        '''
        target = {'url': self.url}
        target.update(**extra_data)
        return target

    def write(self, request, user, data, new=False, message=None):
        '''Write a file into the repository

        When ``new`` the file must not exist, when not
        ``new``, the file must exist.
        '''
        name = data['name']
        path = self.path
        filepath = os.path.join(path, self._format_filename(name))
        if new:
            if not message:
                message = "Created %s" % name
            if os.path.isfile(filepath):
                raise DataError('%s not available' % name)
            else:
                dir = os.path.dirname(filepath)
                if not os.path.isdir(dir):
                    os.makedirs(dir)
        else:
            if not message:
                message = "Updated %s" % name
            if not os.path.isfile(filepath):
                raise DataError('%s not available' % name)

        content = self.content(data)

        # write file
        with open(filepath, 'wb') as f:
            f.write(_b(content))

        filename = get_rel_dir(filepath, self.repo.path)

        add(self.repo, [filename])
        committer = user.username if user.is_authenticated() else 'anonymous'
        commit_hash = commit(self.repo, _b(message), committer=_b(committer))

        return dict(hash=commit_hash.decode('utf-8'),
                    body=content,
                    filename=filename,
                    name=name)

    def delete(self, request, user, data, message=None):
        '''Delete file(s) from repository
        '''
        files_to_del = data.get('files')
        if not files_to_del:
            raise DataError('Nothing to delete')
        # convert to list if not already
        if not isinstance(files_to_del, (list, tuple)):
            files_to_del = [files_to_del]

        filenames = []
        path = self.path

        for file in files_to_del:
            filepath = os.path.join(path, self._format_filename(file))
            # remove only files that really exist and not dirs
            if os.path.exists(filepath) and os.path.isfile(filepath):
                # remove from disk
                os.remove(filepath)
                filename = get_rel_dir(filepath, self.repo.path)
                filenames.append(filename)

        if filenames:
            rm(self.repo, filenames)
            if not message:
                message = 'Deleted %s' % ';'.join(filenames)

            return commit(self.repo, _b(message),
                          committer=_b(user.username))

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
            path = self._path(request, name)
            return reader.process(content, path, src=src,
                                  meta=self.content_meta)
        except IOError:
            raise DataError('%s not available' % name)

    def all(self, request):
        '''Return list of all files stored in repo
        '''
        path = self.path
        files = glob.glob(os.path.join(path, '*.%s' % self.ext))
        for file in files:
            filename = get_rel_dir(file, path)
            yield self.read(request, filename).json(request)

    def serialise_model(self, request, data, in_list=False, **kw):
        if in_list:
            data.pop('html', None)
            data.pop('site', None)
        return data

    def _content(self, request, name):
        '''Read content from file in the repository
        '''
        name = self._format_filename(name)
        path = self.path
        src = os.path.join(path, name)
        # use dulwich GitFile to obeys the git file locking protocol
        with GitFile(src, 'rb') as f:
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
        '''Append extension to file name
        '''
        return remove_double_slash('/%s/%s' % (self.url, path))

    def content(self, data):
        body = data['body']
        return body


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
