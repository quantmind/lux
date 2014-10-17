import os
import shutil

import lux


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.sitemap',
              'lux.extensions.oauth',
              'lux.extensions.angular',
              'lux.extensions.gae']


cfgfile = 'luxpy/extensions/gaesite'
base = 'tests/' + cfgfile + '/'


class Extension(lux.Extension):

    def middleware(self, app):
        return []
