'''
Include Sphinx json files into a static website
'''
import os

from pulsar import ImproperlyConfigured

from lux.extensions import angular

from ..builder import DirBuilder, get_rel_dir
try:
    from .builder import LuxBuilder, LuxSphinx
except ImportError:
    LuxSphinx = None


class SphinxDocs(angular.Router, DirBuilder):
    builddir = '_build'

    def __init__(self, route, dir=None, **params):
        route = self.valid_route(route, dir)
        route = '%s<path:path>' % route
        super(SphinxDocs, self).__init__(route, **params)

    def build(self, app, location=None):
        '''Build the files for this Builder
        '''
        if location is None:
            location = os.path.abspath(app.config['STATIC_LOCATION'])
        if self.built is not None:
            return self.built
        self.built = []
        if not LuxSphinx:
            return self.built
        srcdir = os.path.abspath(self.dir)
        doctreedir = '%s/doctrees' % self.builddir
        app = LuxSphinx(app, srcdir, srcdir, location, doctreedir, 'lux')
        force_all = False
        app.build(force_all)
        return self.built
