import os
import json
import shutil
from string import Template

import lux
from lux.utils.files import skipfile


SKIPDIRS = set(('templates', 'build'))


def skipdir(path):
    name = os.path.basename(path)
    return skipfile(name) or not os.path.isdir(path) or name in SKIPDIRS


class Command(lux.Command):

    help = ('Creates a Lux project configuration files for javascript')
    src = 'js'

    def run(self, options):
        #
        # SCSS first
        self.media('scss', self.scss_target)

        #
        # Javascript second
        base = self.app_base()
        current = os.getcwd()
        os.chdir(base)
        try:
            sources = self.media('js', self.js_target)
            #
            self.write('Create build require config')
            paths = {}
            for name, _ in sources:
                paths.update(self.grunt(name, self.js_target(name)))
            paths.update(self.grunt('', self.app_base()))

            self.save_config_paths(paths)
        finally:
            os.chdir(current)

    def media(self, media, get_target):
        target = get_target()
        if os.path.isdir(target):
            shutil.rmtree(target)
        sources = [('lux', os.path.join(lux.PACKAGE_DIR, 'media', media))]
        for ext in self.app.extensions.values():
            if ext.meta.media_dir:
                src = os.path.join(ext.meta.media_dir, media)
                if os.path.isdir(src):
                    name = ext.meta.name.split('.')[-1]
                    sources.append((name, src))

        for name, src in sources:
            self._copy(src, get_target(name))

        return sources

    def grunt(self, prefix, base):
        '''Create required paths for prefix
        '''
        paths = self.process_files(prefix, base, base)

        for name in os.listdir(base):
            full_path = os.path.join(base, name)
            if not skipdir(full_path):
                paths.update(self.process_files(prefix, base, full_path, name))

        return paths

    def process_files(self, prefix, base, full_path, name=None):
        paths = {}

        templates = os.path.join(full_path, 'templates')
        if os.path.isdir(templates):
            paths.update(self.templates(templates, prefix, base, name))

        if prefix:
            for dirpath, dirnames, filenames in os.walk(full_path):
                relpath = os.path.relpath(dirpath, full_path)
                if relpath == '.':
                    relpath = ''

                if not name and relpath:
                    continue

                for filename in filenames:
                    if skipfile(filename) or not filename.endswith('.js'):
                        continue
                    filename = filename[:-3]
                    path = prefix
                    if name:
                        path = '%s/%s' % (path, name) if path else name
                    if relpath:
                        path = '%s/%s' % (path, relpath) if path else relpath
                    if filename != 'main':
                        path = '%s/%s' % (path, filename) if path else filename
                    assert path, "path not available"
                    assert path not in paths, "path %s already in paths" % path
                    paths[path] = os.path.join(dirpath, filename)

        return paths

    def templates(self, templates, prefix, base, name):
        '''Create the templates directory with valid angular template modules
        '''
        target_dir = self.js_target(prefix, 'templates')
        name = name or prefix
        file_name = '%s/%s/templates' % (prefix, name)
        module_name = '%s.%s.templates' % (prefix, name)
        paths = {}
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
            target = os.path.join(target_dir, '%s.js' % name)

            cache = '\n'.join(cache)
            template = self.template('template.module.js')
            template = template.safe_substitute(
                dict(cache=cache, module_name=module_name)
            )
            with open(target, 'w') as fp:
                fp.write(template)

            self.write('"%s" created' % target)
            paths[file_name] = target[:-3]

        return paths

    def save_config_paths(self, paths):
        # Save lux.json for building the javascript file
        entry = dict(paths=paths)
        lux_cfg = self.js_target('lux.json')
        with open(lux_cfg, 'w') as fp:
            fp.write(json.dumps(entry, indent=4))
        self.write('"%s" created' % lux_cfg)

        #
        # Create Karma files
        cfg_paths = {}
        base = self.js_target_base()
        for name, path in paths.items():
            relpath = os.path.relpath(path, base)
            cfg_paths[name] = relpath
        # Test config
        test_template = self.template('test.config.js')
        test_cfg = self.js_target('test.config.js')
        media_dir = os.path.join(self.app.meta.media_dir,
                                 self.app.config_module, '')
        test_file = test_template.safe_substitute(
            {'media_dir': media_dir,
             'require_paths': json.dumps(cfg_paths, indent=4)})
        with open(test_cfg, 'w') as fp:
            fp.write(test_file)
        self.write('"%s" created' % test_cfg)

    def app_base(self):
        '''Base package directory
        '''
        return os.path.dirname(self.app.meta.path)

    def scss_target(self, *args):
        base = os.path.join(self.app_base(), 'scss', 'deps')
        return self._join_paths(base, *args)

    def js_target(self, *args):
        dir = os.path.join(self.js_target_base(), 'build')
        return self._join_paths(dir, *args)

    def js_target_base(self):
        return os.path.join(self.app_base(), 'js')

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
        if os.path.isdir(target):
            shutil.rmtree(target)
        shutil.copytree(src, target)


def escape_quote(text):
    return text.replace('"', '\\"')
