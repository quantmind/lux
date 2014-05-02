import os
import shutil
import json
from datetime import datetime

from pulsar import Setting

import lux
from lux.extensions.static.builder import build_snippets


class Command(lux.Command):
    help = "create the static site"

    def run(self, options):
        app = self.app
        config = app.config
        request = app.wsgi_request()
        path = app.meta.path
        cur_path = os.curdir
        os.chdir(app.meta.path)
        #options = self.options(argv)
        location = config['STATIC_LOCATION']
        if not os.path.isdir(location):
            os.makedirs(location)
        #
        info = self.build_info()
        context = dict((('site_%s' % k, v) for k, v in info.items()))
        contents = yield from build_snippets(app, context)
        contents.update(context)
        self.create_media()
        self.copy_files(config['EXTRA_FILES'])
        yield from self.build(contents)

    def build(self, contents):
        location = os.path.abspath(self.app.config['STATIC_LOCATION'])
        app = self.app
        config = app.config
        for name, content in sorted(config['STATIC_SITEMAP'].items(),
                                    key=lambda x: x[1].creation_counter):
            yield from content(app, name, location, contents)

    def create_media(self):
        location = os.path.abspath(self.app.config['STATIC_LOCATION'])
        media_dir = os.path.join(location, 'media')
        if os.path.isdir(media_dir):
            self.logger.info('Removing media directory "%s"', media_dir)
            shutil.rmtree(media_dir)
        self.logger.info('Creating media directory "%s"', media_dir)
        os.makedirs(media_dir)
        self.copy_media(media_dir, lux.PACKAGE_DIR, 'lux')
        for ext in self.app.extensions.values():
            self.copy_media(media_dir, ext.meta.path, ext.meta.name)

    def copy_files(self, files):
        location = os.path.abspath(self.app.config['STATIC_LOCATION'])
        for src in files:
            if os.path.isfile(src):
                dst = os.path.join(location, src)
                self.logger.info('Copying %s into %s', src, dst)
                shutil.copyfile(src, dst)
            else:
                self.logger.warning('File %s does not exist', src)

    def copy_media(self, media_dir, path, name):
        src = os.path.join(path, 'media', name)
        if os.path.isdir(src):
            dst = os.path.join(media_dir, name)
            self.logger.info('Copying media directory %s into %s'
                             % (src, dst))
            shutil.copytree(src, dst)

    def build_info(self):
        app = self.app
        cfg = app.config
        location = os.path.abspath(cfg['STATIC_LOCATION'])
        filename = os.path.join(location, 'buildinfo.json')
        dte = datetime.now()
        url = cfg['SITE_URL'] or ''
        if url.endswith('/'):
            url = url[:-1]
        info = {
            'date': dte.strftime(app.config['DATE_FORMAT']),
            'year': dte.year,
            'lux_version': lux.__version__,
            'url': url,
            'media': cfg['MEDIA_URL'][:-1]
        }
        with open(filename, 'w') as f:
            json.dump(info, f, indent=4)
        return info
