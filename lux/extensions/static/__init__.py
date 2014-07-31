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
import sys
import json
import shutil
from datetime import datetime

from pulsar import ImproperlyConfigured
from pulsar.apps.wsgi import FileRouter, WsgiHandler, MediaRouter
from pulsar.utils.slugify import slugify

import lux
from lux import Parameter, Router

from .builder import Builder, DirBuilder, ContextBuilder, get_rel_dir
from .contents import Snippet, Article, Draft
from .routers import (MediaBuilder, HtmlContent, Blog, ErrorRouter,
                      JsonRoot, JsonContent, JsonRedirect)
from .ui import add_css


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
        Parameter('MD_EXTENSIONS', ['extra', 'meta'],
                  'List/tuple of markdown extensions'),
        Parameter('STATIC_API', 'api',
                  'Use angular router in Html5 mode'),
        Parameter('STATIC_SPECIALS', ('404',), '')
    ]
    _static_info = None
    _static_info = None

    def middleware(self, app):
        path = app.config['MEDIA_URL']
        api_url = app.config['STATIC_API']
        if api_url.startswith('/'):
            api_url = api_url[1:]
        if api_url.endswith('/'):
            api_url = api_url[:-1]
        assert api_url, 'STATIC_API must be defined'
        app.api = JsonRoot(app.config['STATIC_API'])
        return [app.api, JsonRedirect(api_url),
                MediaBuilder(path, app.meta.media_dir,
                             show_indexes=app.debug)]

    def on_loaded(self, app):
        '''Once the app is fully loaded add API routes if required
        '''
        self._static_context = None
        middleware = app.handler.middleware
        app.handler.middleware = []
        for router in middleware:
            self.add_api(app, router)
            app.handler.middleware.append(router)

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
            if isinstance(middleware, Builder):
                middleware.build(app, location)
        #
        if self._static_info:
            filename = os.path.join(location, 'buildinfo.json')
            with open(filename, 'w') as f:
                json.dump(self._static_info, f, indent=4)

            self.copy_redirects(request, location)

    def jscontext(self, request, context):
        '''Add api Urls
        '''
        app = request.app
        context.update(self.build_info(app))
        if request.config['STATIC_API']:
            apiUrls = context.get('apiUrls', {})
            for middleware in app.handler.middleware:
                if isinstance(middleware, Router):
                    middleware.add_api_urls(request, apiUrls)
            context['apiUrls'] = apiUrls

    def context(self, request, context):
        if not self._static_context:
            app = request.app
            self._static_context = ctx = self.build_info(app)
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
                        src = os.path.join(dirpath, filename)
                        content = builder.read_file(app, src, name)
                        builder(app, content, ctx)
            else:
                self.logger.warning('Context location "%s" not available', src)
            for c in builder.waiting:
                self.logger.warning('Context "%s" not built, requires %s',
                                    c.name, c.require_context)
        context.update(self._static_context)

    def build_info(self, app):
        '''Return a dictionary with information about the build
        '''
        if not self._static_info:
            cfg = app.config
            dte = datetime.now()
            url = cfg['SITE_URL'] or ''
            if url.endswith('/'):
                url = url[:-1]
            self._static_info = {
                'date': dte.strftime(app.config['DATE_FORMAT']),
                'year': dte.year,
                'lux_version': lux.__version__,
                'python_version': '.'.join((str(v) for v in sys.version_info[:3])),
                'url': url,
                'media': cfg['MEDIA_URL'][:-1],
                'name': cfg['APP_NAME']
            }
        return dict((('site_%s' % k, v) for k, v in self._static_info.items()))

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

    def add_api(self, app, router):
        if isinstance(router, DirBuilder):
            router.api = JsonContent(router.rule, dir=router.dir,
                                     html_router=router)
            app.api.add_child(router.api)
            app.handler.middleware.append(JsonRedirect(router.api.route))
            for route in router.routes:
                self.add_api(app, route)


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
