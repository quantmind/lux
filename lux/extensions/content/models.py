import os

from dulwich.repo import Repo, NotGitRepository

from lux.extensions import rest


class DataError(Exception):
    pass


class Content(rest.RestModel):
    '''A Rest model with git backend using dulwich_

    Several hints for implementation were from gittle_

    .. _dulwich: https://www.samba.org/~jelmer/dulwich/docs/
    .. _gittle: https://github.com/FriendCode/gittle
    '''
    def __init__(self, name, path, **kwargs):
        try:
            self.repo = Repo(path)
        except NotGitRepository:
            self.repo = Repo.init(path)
        self.path = path
        super().__init__(name, **kwargs)

    def write(self, user, data, new=False, message=None):
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
        with open(filename, 'w') as file:
            file.write(content)

        if new:
            self.gittle.add(filename)

        if not message:
            message = "Updated %s" % slug

        ret = self.gittle.commit(name=user.username,
                                 email=user.email,
                                 message=message,
                                 files=[filename])

        # cache.delete(cname)

        return ret

    def all(self):
        index = self.repo.open_index()
        for name in index:
            yield dict(name=name,
                       filename=name,
                       ctime=index[name].ctime[0],
                       mtime=index[name].mtime[0],
                       sha=index[name].sha,
                       size=index[name].size)

    def content(self, data):
        body = data['body']
        return body
