import os
import json
import shutil
from string import Template

import lux
from lux.utils.files import skipfile


class Url:

    def __init__(self, build, test):
        self.build = build
        self.test = test


class Command(lux.Command):

    help = ('Creates a Lux project configuration files for javascript')

    def run(self, options):
        #
        # Lux package
        base = os.path.join(lux.PACKAGE_DIR, 'media')
        paths = self.grunt('lux', base)
        #
        # App package
        paths.update(self.grunt('', self.app.meta.media_dir))

        self.save_config_paths(paths)

    def grunt(self, prefix, base):
        # Clean up build destination
        target = self.target(prefix) if prefix else self.target()
        if os.path.isdir(target):
            shutil.rmtree(target)

        source = os.path.join(base, 'js')
        paths = self.process_files(prefix, base, source)

        for name in os.listdir(source):
            full_path = os.path.join(source, name)
            if (skipfile(name) or not os.path.isdir(full_path)
                    or name == 'templates'):
                continue

            paths.update(self.process_files(prefix, base, full_path, name))

        return paths

    def process_files(self, prefix, base, full_path, name=None):
        paths = {}

        templates = os.path.join(full_path, 'templates')
        if os.path.isdir(templates):
            paths.update(self.templates(templates, prefix, base, name))

        for dirpath, dirnames, filenames in os.walk(full_path):

            relpath = []
            while len(dirpath) > len(full_path):
                dirpath, bit = os.path.split(dirpath)
                relpath.append(bit)
            relpath = '/'.join(relpath)

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
                paths[path] = os.path.join(dirpath, filename)

        return paths

    def target(self, *args):
        build_dir = os.path.join(self.app.meta.media_dir, 'build')
        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)
        return os.path.join(build_dir, *args) if args else build_dir

    def templates(self, templates, prefix, base, name):
        '''Create a template file for angular
        '''
        target_dir = self.target(prefix, 'templates')
        name = name or prefix
        module_name = '%s/%s/templates' % (prefix, name)
        paths = {}
        cache = []
        cache_template = self.template('template.cache.js')

        for filename in os.listdir(templates):
            if filename.endswith('.tpl.html'):
                with open(os.path.join(templates, filename), 'r') as fp:
                    text = fp.read()
                file_module_name = '%s/%s' % (module_name, filename)
                text = ' +\n'.join(self.lines(text))
                cache.append(cache_template.safe_substitute(
                    dict(text=text, module_name=file_module_name)))

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
            paths[module_name] = target[:-3]

        return paths

    def save_config_paths(self, paths):
        cfg_paths = {}
        bases = [os.path.dirname(lux.PACKAGE_DIR),
                 os.path.basename(self.app.meta.path)]
        for name, path in paths.items():
            for base in bases:
                if path.startswith(base):
                    path = path[len(base):]
                    cfg_paths[name] = '/base%s' % path
                    break

        entry = dict(paths=paths)
        lux_cfg = self.target('lux.json')
        with open(lux_cfg, 'w') as fp:
            fp.write(json.dumps(entry, indent=4))
        self.write('"%s" created' % lux_cfg)

        # Test config
        test_template = self.template('test.config.js')
        test_cfg = self.target('test.config.js')
        media_dir = os.path.join(self.app.meta.media_dir,
                                 self.app.config_module, '')
        test_file = test_template.safe_substitute(
            {'media_dir': media_dir,
             'require_paths': json.dumps(cfg_paths, indent=4)})
        with open(test_cfg, 'w') as fp:
            fp.write(test_file)
        self.write('"%s" created' % test_cfg)

    def template(self, name):
        filename = os.path.join(lux.PACKAGE_DIR, 'media', 'templates', name)
        with open(filename, 'r') as fp:
            return Template(fp.read())

    def lines(self, text):
        for line in text.split('\n'):
            yield '         "%s\\n"' % escape_quote(line)


def escape_quote(text):
    return text.replace('"','\\"')