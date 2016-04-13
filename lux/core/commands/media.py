import os
import distutils.core
from string import Template

import lux
from lux.core import LuxCommand, Setting
from lux.utils.files import skipfile


SKIPDIRS = set(('templates', 'build'))


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
        build = MediaBuilder(self, options.js_src, options.scss_src)
        build()


class MediaBuilder:

    def __init__(self, cmd, js_src, scss_src):
        self.write = cmd.write
        self.app = cmd.app
        self.js_src = js_src
        self.scss_src = scss_src

    def __call__(self):
        # SCSS first
        self.media('scss', self.scss_target)
        # JS second
        for name, src in self.media('js', self.js_target):
            self.process_js(name, src)
        self.process_js('', self.app_base())

    def media(self, media, get_target):
        sources = [('lux', os.path.join(lux.PACKAGE_DIR, 'media', media))]
        for ext in self.app.extensions.values():
            if ext.meta.name != self.app.meta.name and ext.meta.media_dir:
                src = os.path.join(ext.meta.media_dir, media)
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

    def process_js(self, prefix, src):
        """Create required paths for ``prefix``

        :param prefix: the name of the library (lux, mylib, ...)
        :param src: the source folder for ``prefix``
        :param target: the directory where to place files which need building
            (for example templates)
        """
        self.js_templates(prefix, src)

        for name in os.listdir(src):
            src_name = os.path.join(src, name)
            if not skipdir(src_name):
                self.js_templates(prefix, src_name, name)

    def js_templates(self, prefix, src, name=None):
        """
        :param prefix: the library name (lux, mylib, ...)
        :param src: the source directory of files
        :param name: when ``None`` don't recursively walk subpaths
        :return: a dictionary for requirejs
        """
        templates = os.path.join(src, 'templates')
        if not os.path.isdir(templates):
            return

        tmpl = 'templates'
        bits = [prefix]
        if name:
            bits.append(name)
        target_dir = self.js_target(*bits)
        bits.append(tmpl)
        file_name = '/'.join(bits)
        module_name = '.'.join(bits)
        cache = []
        cache_template = self.template('template.cache.js')

        for filename in os.listdir(templates):
            if filename.endswith('.tpl.html'):
                with open(os.path.join(templates, filename), 'r') as fp:
                    text = fp.read()
                file_module_name = '%s/%s' % (file_name, filename)
                text = ' +\n'.join(self.lines(text))
                cache.append(cache_template.safe_substitute(
                    dict(text=text, file_name=file_module_name)))

        if cache:
            if not os.path.isdir(target_dir):
                os.makedirs(target_dir)
            target = os.path.join(target_dir, '%s.js' % tmpl)

            cache = '\n'.join(cache)
            template = self.template('template.module.js')
            template = template.safe_substitute(
                dict(cache=cache, module_name=module_name)
            )
            with open(target, 'w') as fp:
                fp.write(template)

            self.write('"%s" created' % target)

    def app_base(self):
        '''Base package directory
        '''
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

    def lines(self, text):
        for line in text.split('\n'):
            yield '         "%s\\n"' % escape_quote(line)

    def _join_paths(self, dir, *args):
        dir = os.path.join(dir, *args) if args else dir
        return dir

    def _copy(self, src, target):
        self.write('Copy files from "%s" to "%s"' % (src, target))
        distutils.dir_util.copy_tree(src, target, verbose=0)


def escape_quote(text):
    return text.replace('"', '\\"')


def skipdir(path):
    name = os.path.basename(path)
    return skipfile(name) or not os.path.isdir(path) or name in SKIPDIRS
