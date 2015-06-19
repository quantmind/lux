import os
import glob

from dulwich.file import GitFile
from dulwich.porcelain import rm
from dulwich.porcelain import add
from dulwich.porcelain import init
from dulwich.porcelain import commit
from dulwich.porcelain import open_repo
from dulwich.errors import NotGitRepository

from lux.extensions import rest


def _b(value):
    '''Return string literals
    '''
    return value.encode('utf-8')


class DataError(Exception):
    pass


class Content(rest.RestModel):

    '''A Rest model with git backend using dulwich_

    This model provide basic CRUD operations for a RestFul web API

    .. _dulwich: https://www.samba.org/~jelmer/dulwich/docs/
    '''

    def __init__(self, name, path, **kwargs):
        try:
            self.repo = open_repo(path)
        except NotGitRepository:
            self.repo = init(path)
        self.path = path
        super().__init__(name, **kwargs)

    def write(self, user, data, new=False, message=None):
        '''Write a file into the repository
        '''
        slug = data['slug']
        filename = '%s.md' % slug
        fullpath = os.path.join(self.path, filename)
        if new:
            if not message:
                message = "Created %s" % slug
            if os.path.isfile(fullpath):
                raise DataError('%s not available' % slug)
        else:
            if not message:
                message = "Updated %s" % slug
            if not os.path.isfile(fullpath):
                raise DataError('%s not available' % slug)

        content = self.content(data)

        with open(fullpath, 'wb') as f:
            f.write(_b(content))

        add(self.repo, [filename])
        commit_hash = commit(self.repo, _b(message),
                             committer=_b(user.username))
        return commit_hash

    def delete(self, user, data, message=None):
        '''Delete file(s) from repository
        '''
        files_to_del = data.get('files')
        if files_to_del:
            for f in files_to_del:
                path = os.path.join(self.path, f)
                # remove only files that really exist
                if os.path.exists(path):
                    # remove from disk
                    os.remove(path)
                    # remove from repo
                    rm(self.repo, [path])
            if not message:
                message = 'Deleted %s' % ';'.join(files_to_del)
                commit_hash = commit(self.repo, _b(message),
                                     committer=_b(user.username))
                return commit_hash
        raise DataError('Nothing to delete')

    def read(self, path):
        '''Read content from file in repository
        '''
        if not os.path.isabs:
            path = os.path.join(self.repo.path, path)
        if os.path.exists(path):
            # use GitFile instead of standard file object, as it gives
            # `lazy` behavior and also obeys the git file locking protocol
            with GitFile(path) as f:
                content = f.read()
            return content.decode('utf-8')
        raise DataError('%s not available' % path)

    def all(self):
        return glob.glob(os.path.join(self.repo.path, '*.md'))

    def content(self, data):
        body = data['body']
        return body
