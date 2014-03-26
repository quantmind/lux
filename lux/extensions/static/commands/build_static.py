import os
import shutil

from pulsar import Setting

import lux


class Command(lux.Command):
    help = "create the site model"

    def run(self, argv):
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
        sitemap = config['STATIC_SITEMAP']
        self.create_media()
        self.copy_files(config['EXTRA_FILES'])
        yield from self.build()

    def build(self):
        location = os.path.abspath(self.app.config['STATIC_LOCATION'])
        app = self.app
        config = app.config
        for name, content in sorted(config['STATIC_SITEMAP'].items(),
                                    key=lambda x: x[1].creation_counter):
            for file_name, data in content(app, name):
                data = yield from data
                dst = os.path.join(location, file_name)
                dirname = os.path.dirname(dst)
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)
                self.logger.info('Creating "%s"', dst)
                with open(dst, 'w') as f:
                    f.write(data)

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
