from pulsar.utils.pep import ispy3k, pypy
__test__ = not (ispy3k or pypy)

import lux
from lux.extensions.cms import CMS
from lux.extensions.cms.gae import PageManager


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.api',
              'lux.extensions.angular']
              #'lux.extensions.sessions']


class Extension(lux.Extension):

    def middleware(self, app):
        manager = app.api.createManager(app, PageManager)
        return [CMS('/', manager=manager)]

