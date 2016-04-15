import os
import shutil

from tests.config import *  # noqa

from lux.core import LuxExtension
from lux.extensions.content import Content, CMS


CONTENT_LOCATION = os.path.join(os.path.dirname(__file__), 'test_repo')

GITHUB_HOOK_KEY = 'test12345'

EXTENSIONS = ['lux.extensions.rest',
              'lux.extensions.content']


def remove_repo():
    shutil.rmtree(CONTENT_LOCATION)


def create_content(name, path=None):
    path = os.path.join(path or CONTENT_LOCATION, name)
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(os.path.join(path, 'index.md'), 'w') as fp:
        fp.write('\n'.join(('title: Index', '', 'Just an index')))
    with open(os.path.join(path, 'foo.md'), 'w') as fp:
        fp.write('\n'.join(('title: This is Foo', '', 'Just foo')))


class Extension(LuxExtension):

    def middleware(self, app):
        repo = app.config['CONTENT_LOCATION']
        app.cms = CMS(app)
        app.cms.add_router(Content('blog', repo))
        app.cms.add_router(Content('site', repo, ''))
        return app.cms.middleware()
