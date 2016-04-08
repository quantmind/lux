import os

from lux.core import LuxExtension
from lux.extensions.content import Content
from lux.utils.data import update_dict

__test__ = False

PATH = os.path.dirname(__file__)


meta = {'image': '/media/lux/see.jpg'}
articles_meta = update_dict(meta, {})
site_meta = update_dict(meta, {})


class Extension(LuxExtension):

    def on_config(self, app):
        '''Register Content models
        '''
        app.models.register(Content('articles', PATH,
                                    content_meta=articles_meta))
        app.models.register(Content('site', PATH, '',
                                    content_meta=site_meta))
