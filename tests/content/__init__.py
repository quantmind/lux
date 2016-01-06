import os
import shutil

from tests.config import *  # noqa

import lux
from lux.extensions.content import TextCRUD, Content, GithubHook, CMS


PWD = os.path.join(os.path.dirname(__file__), 'test_repo')

GREEN_POOL = 100

EXTENSIONS = ['lux.extensions.rest',
              'lux.extensions.content']


def remove_repo():
    shutil.rmtree(PWD)


class Extension(lux.Extension):

    def middleware(self, app):
        app.cms = CMS(app)
        app.cms.add_router(Content('blog', PWD))
        middleware = [GithubHook('refresh-content', secret='test12345')]
        middleware.extend(app.cms.middleware())
        return middleware
