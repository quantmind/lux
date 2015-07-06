import os
import glob

from dulwich.porcelain import rm
from dulwich.porcelain import add
from dulwich.porcelain import init
from dulwich.porcelain import commit
from dulwich.porcelain import open_repo
from dulwich.file import GitFile
from dulwich.errors import NotGitRepository

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

    def __init__(self, name, repo, path=None, ext='md', **kwargs):
        try:
            self.repo = open_repo(repo)
        except NotGitRepository:
            self.repo = init(repo)
        self.path = repo
        self.ext = ext
        if path is None:
            path = name
        if path:
            self.path = os.path.join(self.path, path)
        super().__init__(name, **kwargs)

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
        filepath = self._format_filename(slug)
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
        return commit_hash.decode('utf-8')

    def delete(self, user, data, message=None):
        '''Delete file(s) from repository
        '''
        files_to_del = data.get('files')
        if not files_to_del:
            raise DataError('Nothing to delete')
        # convert to list if not already
        if not isinstance(files_to_del, (list, tuple)):
            files_to_del = [files_to_del]

        filenames = self._format_filename(files_to_del)
        for f in filenames:
            # remove only files that really exist and not dirs
            if os.path.exists(f) and os.path.isfile(f):
                # remove from disk
                os.remove(f)
                # remove from repo, we need only file name not full path
                name = f.split('/')[-1]
                rm(self.repo, [name])

        if not message:
            message = 'Deleted %s' % ';'.join(filenames)

        commit_hash = commit(self.repo, _b(message),
                             committer=_b(user.username))
        return commit_hash

    def read(self, filename):
        '''Read content from file in repository
        '''
        path = self._format_filename(filename)
        try:
            # use dulwich GitFile to obeys the git file locking protocol
            with GitFile(path, 'rb') as f:
                content = f.read()
            return dict(content=content.decode('utf-8'),
                        filename=filename,
                        path=path)
        except IOError:
            raise DataError('%s not available' % filename)

    def all(self):
        '''Return list of all files stored in repo
        '''
        files = glob.glob(os.path.join(self.repo.path, '*.%s' % self.ext))
        return self._get_filename(files)

    def _iter_filename(self, filename, func, path=None):
        '''In case more than one filename is provided, normalize
        all entries by provided function. Dedicated for `_format_filename'
        and `_get_filename` functions, should be not use directly.
        '''
        _filename = []
        for name in filename:
            if path:
                _name = func(name, path)
            else:
                _name = func(name)
            _filename.append(_name)
        return _filename

    def _format_filename(self, filename):
        '''Append `.md` extension to file name and full path
        if `path` is True.
        '''
        if isinstance(filename, (list, tuple)):
            return self._iter_filename(filename, self._format_filename)

        ext = '.%s' % self.ext
        if not filename.endswith(ext):
            filename = '%s%s' % (filename, ext)
        return os.path.join(self.path, filename)

    def _get_filename(self, filename):
        '''Get rid of full path and `.md` extension and
        return peeled file name.
        '''
        if isinstance(filename, (list, tuple)):
            return self._iter_filename(filename, self._get_filename)

        # in case filename is a full path to a file
        filename = filename.split('/')[-1]
        if filename.endswith('.md'):
            filename = filename[:-3]
        return filename

    def content(self, data):
        body = data['body']
        return body
