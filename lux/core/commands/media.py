import os
import distutils.core
from string import Template

import lux
from lux.core import LuxCommand, Setting


class Command(LuxCommand):
    option_list = (
        Setting('js_src', ('--js-src',),
                default='js',
                desc=('Javascript source directory')),
        Setting('scss_src', ('--scss-src',),
                default='scss/deps',
                desc=('SASS CSS source directory')),
    )

    help = ('Creates a lux project configuration files for javascript and '
            'scss compilation')

    def run(self, options):
        MediaBuilder(self, options.js_src, options.scss_src)()


class MediaBuilder:

    def __init__(self, cmd, js_src, scss_src):
        self.write = cmd.write
        self.app = cmd.app
        self.js_src = js_src
        self.scss_src = scss_src

    def __call__(self):
        self.media('scss', self.scss_target)
        self.media('js', self.js_target)

    def media(self, media, get_target):
        sources = [('lux', os.path.join(lux.PACKAGE_DIR, media))]
        for ext in self.app.extensions.values():
            if ext.meta.name != self.app.meta.name:
                src = os.path.join(ext.meta.path, media)
                if os.path.isdir(src):
                    name = ext.meta.name.split('.')[-1]
                    sources.append((name, src))

        targets = []
        for name, src in sources:
            target = get_target(name)
            self._copy(src, target)
            targets.append((name, target))
        sources = targets

        return sources

    def app_base(self):
        return os.getcwd()

    def scss_target(self, *args):
        base = os.path.join(self.app_base(), self.scss_src)
        return self._join_paths(base, *args)

    def js_target(self, *args):
        base = os.path.join(self.app_base(), self.js_src)
        return self._join_paths(base, *args)

    def template(self, name):
        filename = os.path.join(lux.PACKAGE_DIR, 'media', 'templates', name)
        with open(filename, 'r') as fp:
            return Template(fp.read())

    def _join_paths(self, dir, *args):
        dir = os.path.join(dir, *args) if args else dir
        return dir

    def _copy(self, src, target):
        self.write('Copy files from "%s" to "%s"' % (src, target))
        distutils.dir_util.copy_tree(src, target, verbose=0)
