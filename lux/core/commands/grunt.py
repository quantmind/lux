import os
import json

import lux


COMPONENTS = [
    "services",
    "forms",
    "messages",
    "nav"
]


class Command(lux.Command):

    help = ('Creates a Lux project directory structure for the given '
            'project name in the current directory or optionally in the '
            'given directory.')

    def run(self, options):
        # Read media/config.json
        #
        paths = {}
        html2js = {}

        lux_entry = {
            'paths': paths,
            'html2js': html2js
        }
        paths['lux'] = self.js('lux')
        template_dest = os.path.join(self.app.meta.media_dir,
                                     'build', 'templates', 'lux')
        #
        # Loop through lux.js components
        for name in os.listdir(self.js()):
            if name.startswith('.') or name.startswith('_'):
                continue
            full_path = self.js(name)

            if os.path.isdir(full_path):
                templates = os.path.join(full_path, 'templates')
                if os.path.isdir(templates):
                    path = 'lux/%s/templates' % name
                    dest = os.path.join(template_dest, name)
                    html2js[name] = {
                        'src': os.path.join(templates, '*.tpl.html'),
                        'dest': '%s.js' % dest
                    }
                    paths[path] = dest

                for dirpath, dirnames, filenames in os.walk(full_path):
                    relpath = []
                    while len(dirpath) > len(full_path):
                        dirpath, base = os.path.split(dirpath)
                        relpath.append(base)
                    relpath = '/'.join(relpath)

                    for filename in filenames:
                        if not filename.endswith('.js'):
                            continue
                        filename = filename[:-3]
                        path = 'lux/%s' % name
                        if relpath:
                            path = '%s/%s' % (path, relpath)
                        if filename != 'main':
                            path = '%s/%s' % (path, filename)
                        paths[path] = self.js(dirpath, filename)

        lux_cfg = os.path.join(self.app.meta.media_dir, 'lux.json')
        with open(lux_cfg, 'w') as fp:
            fp.write(json.dumps(lux_entry, indent=4))
        self.write('"%s" created' % lux_cfg)

    def js(self, *args):
        return os.path.join(lux.PACKAGE_DIR, 'media', 'js', *args)
