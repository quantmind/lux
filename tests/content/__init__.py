import os
import shutil

from tests.config import *  # noqa

from lux.utils import test


API_URL = '/api'
DEFAULT_CONTENT_TYPE = 'text/html'
CONTENT_REPO = os.path.join(os.path.dirname(__file__), 'test_repo')

GITHUB_HOOK_KEY = 'test12345'

EXTENSIONS = ['lux.extensions.rest',
              'lux.extensions.content']
AUTHENTICATION_BACKENDS = ['lux.core:SimpleBackend']
CONTENT_GROUPS = {
    "blog": {
        "path": "blog",
        "meta": {
            "priority": 1
        }
    },
    "site": {
        "path": "*",
        "meta": {
            "priority": 1,
            "image": "/media/lux/see.jpg"
        }
    }
}


def remove_repo():
    shutil.rmtree(CONTENT_REPO)


def create_content(name):
    path = os.path.join(CONTENT_REPO, name)
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(os.path.join(path, 'index.md'), 'w') as fp:
        fp.write('\n'.join(('title: Index', '', 'Just an index')))
    with open(os.path.join(path, 'foo.md'), 'w') as fp:
        fp.write('\n'.join(('title: This is Foo', '', 'Just foo')))


class Test(test.AppTestCase):
    config_file = 'tests.content'

    @classmethod
    def setUpClass(cls):
        create_content('blog')
        create_content('site')
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        remove_repo()
        return super().tearDownClass()
