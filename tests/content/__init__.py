import os
import shutil

from tests.config import *  # noqa

import lux
from lux.extensions.content import Content, GithubHook, CMS


PWD = os.path.join(os.path.dirname(__file__), 'test_repo')

GREEN_POOL = 100

EXTENSIONS = ['lux.extensions.rest',
              'lux.extensions.content']


def remove_repo():
    shutil.rmtree(PWD)


def create_content(name, path=None):
    path = os.path.join(path or PWD, name)
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(os.path.join(path, 'index.md'), 'w') as fp:
        fp.write('\n'.join(('title: Index', '', 'Just an index')))
    with open(os.path.join(path, 'foo.md'), 'w') as fp:
        fp.write('\n'.join(('title: This is Foo', '', 'Just foo')))


class Extension(lux.Extension):

    def middleware(self, app):
        app.cms = CMS(app)
        app.cms.add_router(Content('blog', PWD))
        app.cms.add_router(Content('site', PWD, ''))
        middleware = [GithubHook('refresh-content', secret='test12345')]
        middleware.extend(app.cms.middleware())
        return middleware
