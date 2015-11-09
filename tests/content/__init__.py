import os
import shutil

from tests.config import *  # noqa

import lux
from lux.extensions.rest import RestModel
from lux.extensions.content import TextCRUD, Content, TextForm, GithubHook


PWD = os.path.join(os.getcwd(), 'test_repo')

GREEN_POOL = 100


EXTENSIONS = ['lux.extensions.rest',
              'lux.extensions.content']


def remove_repo():
    shutil.rmtree(PWD)


class Extension(lux.Extension):

    def middleware(self, app):
        content = Content('blog', PWD, form=TextForm, url='blog')
        return [GithubHook('refresh-content', secret='test12345'),
                TextCRUD(content)]
