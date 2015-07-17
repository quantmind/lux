import os
import shutil

from tests.config import *  # noqa

import lux
from lux.extensions.content import TextCRUD, Content, TextForm, GithubHook


PWD = os.path.join(os.getcwd(), 'test_repo')


EXTENSIONS = ['lux.extensions.rest',
              'lux.extensions.content']


def remove_repo():
    shutil.rmtree(PWD)


class Extension(lux.Extension):

    def middleware(self, app):
        content = Content('blog', PWD, form=TextForm, url='blog')
        return [TextCRUD(content)]

    def async_middleware(self, app):
        return [GithubHook('refresh-content',
                           repo=PWD,
                           secret='test12345')]
