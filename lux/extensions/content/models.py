import os
import glob

from dulwich.porcelain import rm
from dulwich.porcelain import add
from dulwich.porcelain import init
from dulwich.porcelain import commit
from dulwich.porcelain import open_repo
from dulwich.file import GitFile
from dulwich.errors import NotGitRepository

from lux import cached, get_reader
from lux.extensions import rest
from lux.utils.files import get_rel_dir


__all__ = ('_b', 'DataError', 'Content')


def _b(value):
    '''Return string literals
    '''
    return value.encode('utf-8')


class DataError(Exception):
    pass


class Content(rest.RestModel):
    '''A Rest model with git backend using dulwich_

    This model provide basic CRUD operations for a RestFul web API.

    .. _dulwich: https://www.samba.org/~jelmer/dulwich/docs/
    '''
    def __init__(self, name, repo, path=None, ext='md', content_meta=None,
                 **kwargs):
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
        super().__init__(name, **kwargs)

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

    def write(self, user, data, new=False, message=None):
        '''Write a file into the repository

        When ``new`` the file must not exist, when not
        ``new``, the file must exist.
        '''
        slug = data['slug']
        filepath = os.path.join(self.path, self._format_filename(slug))
        if new:
            if not message:
                message = "Created %s" % slug
            if os.path.isfile(filepath):
                raise DataError('%s not available' % slug)
            else:
                dir = os.path.dirname(filepath)
                if not os.path.isdir(dir):
                    os.makedirs(dir)
        else:
            if not message:
                message = "Updated %s" % slug
            if not os.path.isfile(filepath):
                raise DataError('%s not available' % slug)

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
                    slug=slug)

    def delete(self, user, data, message=None):
        '''Delete file(s) from repository
        '''
        files_to_del = data.get('files')
        if not files_to_del:
            raise DataError('Nothing to delete')
        # convert to list if not already
        if not isinstance(files_to_del, (list, tuple)):
            files_to_del = [files_to_del]

        filenames = []

        for file in files_to_del:
            filepath = os.path.join(self.path, self._format_filename(file))
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

    def read(self, request, name):
        '''Read content from file in repository
        '''
        filename = self._format_filename(name)
        path = os.path.join(self.path, filename)
        try:
            # use dulwich GitFile to obeys the git file locking protocol
            with GitFile(path, 'rb') as f:
                content = f.read()

            reader = get_reader(request.app, filename)
            name = self._slug(filename)
            content = reader.process(content, path, name, slug=name,
                                     meta=self.content_meta)
            path = '/%s/%s' % (self.url, content._meta.slug)
            content._meta.url = request.absolute_uri(path)
            return content
        except IOError:
            raise DataError('%s not available' % name)

    def all(self, request):
        '''Return list of all files stored in repo
        '''
        files = glob.glob(os.path.join(self.path, '*.%s' % self.ext))
        for file in files:
            filename = get_rel_dir(file, self.path)
            yield self.read(request, filename).json(request)

    def _format_filename(self, filename):
        '''Append extension to file name
        '''
        ext = '.%s' % self.ext
        if not filename.endswith(ext):
            filename = '%s%s' % (filename, ext)
        return filename

    def _slug(self, filename):
        '''Append extension to file name
        '''
        return filename[:-len(self.ext)-1]

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
        return [d for d in self.model.all(request)
                if d.get('priority') and d.get('order')]


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
