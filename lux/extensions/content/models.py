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

    def write(self, user, data, new=False, message=None):
        '''Write a file into the repository

        When ``new`` the file must not exist, when not
        ``new``, the file must exist.
        '''
        slug = data['slug']
        filename = self._format_filename(slug)
        filepath = self._format_filename(slug, True)
        if new:
            if not message:
                message = "Created %s" % slug
            if os.path.isfile(filepath):
                raise DataError('%s not available' % slug)
        else:
            if not message:
                message = "Updated %s" % slug
            if not os.path.isfile(filepath):
                raise DataError('%s not available' % slug)

        content = self.content(data)

        # write file
        with open(filepath, 'wb') as f:
            f.write(_b(content))

        add(self.repo, [filename])
        commit_hash = commit(self.repo, _b(message),
                             committer=_b(user.username))
        return commit_hash

    def delete(self, user, data, message=None):
        '''Delete file(s) from repository
        '''
        files_to_del = data.get('files')
        if not files_to_del:
            raise DataError('Nothing to delete')
        # convert to list if not already
        if not isinstance(files_to_del, (list, tuple)):
            files_to_del = [files_to_del]

        filenames = self._format_filename(files_to_del, path=True)
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
        file_name = self._format_filename(filename, True)
        try:
            # use dulwich GitFile to obeys the git file locking protocol
            with GitFile(file_name, 'rb') as f:
                content = f.read()
            return content.decode('utf-8')
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

    def _format_filename(self, filename, path=None):
        '''Append `.md` extension to file name and full path
        if `path` is True.
        '''
        if isinstance(filename, (list, tuple)):
            return self._iter_filename(filename, self._format_filename, path)

        ext = '.%s' % self.ext
        if not filename.endswith(ext):
            filename = '%s%s' % (filename, ext)
        if path:
            filename = os.path.join(self.path, filename)
        return filename

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
