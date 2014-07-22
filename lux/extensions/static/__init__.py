'''Static site generator



Usage
=======
Put the ``lux.extensions.static`` extension into your :setting:`EXTENSIONS`
list and build the static web site via the ``build_static`` option in the
command line::

    python managet.py build_static

Parameters
================

.. lux_extension:: lux.extensions.static
'''
import os
import json
import shutil
from datetime import datetime

from pulsar import ImproperlyConfigured
from pulsar.apps.wsgi import FileRouter, WsgiHandler
from pulsar.utils.slugify import slugify

import lux
from lux import Parameter

from .builder import StaticBuilder, ContextBuilder, get_rel_dir
from .contents import Snippet
from .routers import MediaRouter, DirContent, Content, Blog, ErrorRouter
#from .blog import Blog


class StaticHandler(WsgiHandler):
    pass


class Extension(lux.Extension):
    '''The sessions extensions provides wsgi middleware for managing sessions
    and users.

    In addition it provides utilities for managing Cross Site Request Forgery
    protection and user permissions levels.
    '''
    _config = [
        Parameter('STATIC_TEMPLATE', 'home.html',
                  'Default static template'),
        Parameter('SOURCE_SUFFIX', 'md',
                  'The default suffix of source filenames'),
        Parameter('METADATA_PROCESSORS', [],
                  'A list of functions to perocess metadata'),
        Parameter('STATIC_LOCATION', 'build',
                  'Directory where the static site is created'),
        Parameter('STATIC_SITEMAP', {},
                  'Dictionary of contents for the site'),
        Parameter('CONTEXT_LOCATION', 'context',
                  'Directory where to find files to populate the context '
                  'dictionary'),
        Parameter('EXTRA_FILES', (),
                  'List/tuple of additional files to copy to the '
                  ':setting:`STATIC_LOCATION`'),
        Parameter('MD_EXTENSIONS', ['extra', 'meta'],
                  'List/tuple of markdown extensions'),
        Parameter('STATIC_HTML5', True,
                  'Use angular router in Html5 mode'),
        Parameter('STATIC_SPECIALS', ('404',), '')
    ]
    _static_info = None

    def middleware(self, app):
        path = app.config['MEDIA_URL']
        return [MediaRouter(path, app.meta.media_dir, show_indexes=app.debug)]

    def on_loaded(self, app):
        self._static_context = None
        router404 = None
        for router in app.handler.middleware:
            if isinstance(router, StaticBuilder):
                src_dir = router.src or router.route.rule
                if os.path.isdir(src_dir):
                    router.dir = src_dir
                    for url_path, file_path, ext in router.all_files():
                        if url_path == 'index':
                            router.src = file_path

    def on_request(self, app, request):
        if not app.debug and not isinstance(app.handler, StaticHandler):
            app.handler = StaticHandler()
            path = os.path.abspath(app.config['STATIC_LOCATION'])
            middleware = app.handler.middleware
            file404 = os.path.join(path, '404.html')
            if os.path.isfile(file404):
                raise_404 = False
            media = MediaRouter('', path, default_suffix='html',
                                raise_404=raise_404)
            middleware.append(media)
            if not raise_404:
                middleware.append(FileRouter('<path:path>', file404,
                                             status_code=404))

    def build(self, request):
        '''Build the static site
        '''
        app = request.app
        config = request.config
        location = os.path.abspath(config['STATIC_LOCATION'])
        if not os.path.isdir(location):
            os.makedirs(location)
        #
        for middleware in app.handler.middleware:
            if isinstance(middleware, StaticBuilder):
                middleware.build(app, location)
        #
        if self._static_info:
            filename = os.path.join(location, 'buildinfo.json')
            with open(filename, 'w') as f:
                json.dump(self._static_info, f, indent=4)

    def context(self, request, context):
        if not self._static_context:
            app = request.app
            self._static_info = info = self.build_info(app)
            #
            # CONTEXT DICTIONARY
            ctx = dict((('site_%s' % k, v) for k, v in info.items()))
            self._static_context = ctx
            #
            src = app.config['CONTEXT_LOCATION']
            builder = ContextBuilder()
            if os.path.isdir(src):
                for dirpath, _, filenames in os.walk(src):
                    rel_dir = get_rel_dir(dirpath, src)
                    for filename in filenames:
                        if filename.startswith('.'):
                            continue
                        name, _ = os.path.join(rel_dir, filename).split('.', 1)
                        key = slugify(name, separator='_')
                        src = os.path.join(dirpath, filename)
                        builder(app, src, ctx, key)
            else:
                self.logger.warning('Context location "%s" not available', src)
            for c in builder.waiting:
                self.logger.warning('Context "%s" not built, requires %s',
                                    c.name, c.require_context)
        context.update(self._static_context)

    def build_info(self, app):
        '''Return a dictionary with information about the build
        '''
        cfg = app.config
        dte = datetime.now()
        url = cfg['SITE_URL'] or ''
        if url.endswith('/'):
            url = url[:-1]
        return {
            'date': dte.strftime(app.config['DATE_FORMAT']),
            'year': dte.year,
            'lux_version': lux.__version__,
            'url': url,
            'media': cfg['MEDIA_URL'][:-1]
        }

    def __build(self, request):
        '''Build the static site
        '''
        app = request.app
        config = request.config
        path = app.meta.path
        cur_path = os.curdir
        os.chdir(app.meta.path)
        location = os.path.abspath(config['STATIC_LOCATION'])
        if not os.path.isdir(location):
            os.makedirs(location)
        #
        # INFO
        info = self.build_info(request)
        filename = os.path.join(location, 'buildinfo.json')
        with open(filename, 'w') as f:
            json.dump(info, f, indent=4)
        #
        # CONTEXT DICTIONARY
        context = dict((('site_%s' % k, v) for k, v in info.items()))
        self.build_context(request, context)
        #
        # Copy Media, extra files and redirects
        self.create_media(request, location)
        self.copy_redirects(request, location)
        self.copy_files(config['EXTRA_FILES'], location)
        #
        for name, content in config['STATIC_SITEMAP'].items():
            content(request, name, location, context)

    def create_media(self, request, location):
        media_dir = os.path.join(location, 'media')
        if os.path.isdir(media_dir):
            self.logger.info('Removing media directory "%s"', media_dir)
            shutil.rmtree(media_dir)
        self.logger.info('Creating media directory "%s"', media_dir)
        os.makedirs(media_dir)
        self.copy_media(media_dir, lux.PACKAGE_DIR, 'lux')
        for ext in request.app.extensions.values():
            self.copy_media(media_dir, ext.meta.path, ext.meta.name)

    def copy_files(self, files, location):
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

    def copy_redirects(self, request, location):
        '''Reads the ``redirects.json`` file if it exists and
        create redirects files.
        '''
        app = request.app
        name = os.path.join(app.meta.path, 'redirects.json')
        if os.path.isfile(name):
            with open(name) as file:
                redirects = json.loads(file.read())
        else:
            return
        engine = lux.template_engine()
        for origin, target in redirects.items():
            content = engine(REDIRECT_TEMPLATE, {'target': target})
            if origin.startswith('/'):
                origin = origin[1:]
            dst = os.path.join(location, origin)
            dir = os.path.dirname(dst)
            base = os.path.basename(dst)
            if not base:
                dst = os.path.join(dir, 'index')
            if not dst.endswith('.html'):
                dst = '%s.html' % dst
            if not os.path.exists(dir):
                os.makedirs(dir)
            self.logger.info('Redirect %s into %s', origin, dst)
            with open(dst, 'w') as f:
                f.write(content)



REDIRECT_TEMPLATE = '''\
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<script type="text/javascript">
window.location = location.origin + "$target";
</script>
<head>
'''
