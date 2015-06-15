'''Static site generator

**Required extensions**: :mod:`lux.extensions.ui`,
:mod:`lux.extensions.angular`

**Optional third-party libraries**: markdown_, sphinx_


Usage
=======
Put the :mod:`lux.extensions.static` extension into your :setting:`EXTENSIONS`
list and build the static web site via the ``build_static`` option in the
command line::

    python managet.py build_static

There are several :ref:`parameters <parameters-static>` which can be modified
in order to customise the site.

The first step is to create a new project via the :command:`startproject`
command.


When creating the middleware for the static site one can pass the following
key-valued parameters during initialisation of a :class:`.HtmlContent`,
a :class:`.Blog` and other routers:

* ``dir`` the directory where the source files are located, if not provided,
  it is assumed it is the same as the route parameter
* :attr:`~lux.extensions.Html5.Router.html_body_template` to specify the
  location of the template which render the html body tag of the Html5
  document. If not provided, the parent router value is used unless no parent
  is available and the :setting:`STATIC_TEMPLATE` is used instead.

.. _markdown: https://pythonhosted.org/Markdown/
.. _sphinx: http://sphinx-doc.org/
'''
import os
import sys
import json
from datetime import datetime

from pulsar import ImproperlyConfigured
from pulsar.apps.wsgi import FileRouter, WsgiHandler, MediaRouter

import lux
from lux import Parameter, Router

from .builder import Builder, DirBuilder, ContextBuilder, DirContent
from .contents import Content, Article
from .routers import (MediaBuilder, HtmlContent, Blog, ErrorRouter,
                      JsonRoot, JsonRedirect, Sitemap, HtmlFile)
from .readers import register_reader
from .rst import SphinxDocs
from .ui import add_css


__all__ = ['Builder', 'DirBuilder', 'DirContent', 'ErrorRouter',
           'Sitemap', 'HtmlFile', 'Blog', 'Content', 'Article',
           'SphinxDocs', 'register_reader', 'add_css']


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
        Parameter('STATIC_LOCATION', 'build',
                  'Directory where the static site is created'),
        Parameter('CONTEXT_LOCATION', 'context',
                  'Directory where to find files to populate the context '
                  'dictionary'),
        Parameter('STATIC_API', 'api',
                  'Build a JSON api, required when using angular in Html5 '
                  ' navigation mode'),
        Parameter('STATIC_MEDIA', True, 'Add handler for media files'),
        Parameter('STATIC_SPECIALS', ('404',),
                  "paths included in this list won't create the json api")
    ]
    _static_info = None
    _global_context = None

    def middleware(self, app):
        app.thread_pool = False
        app.require('lux.extensions.angular')
        html5 = app.config['HTML5_NAVIGATION']
        path = app.config['MEDIA_URL']
        api_url = app.config['STATIC_API'] or ''
        if api_url.startswith('/'):
            api_url = api_url[1:]
        if api_url.endswith('/'):
            api_url = api_url[:-1]
        if not api_url and html5:
            raise ImproperlyConfigured('STATIC_API url must be defined')
        middleware = []
        app.api = None
        if api_url:
            app.api = JsonRoot(api_url)
            middleware.extend([app.api, JsonRedirect(api_url)])
        if app.config['STATIC_MEDIA']:
            middleware.append(MediaBuilder(path, app.meta.media_dir,
                                           show_indexes=app.debug))
        return middleware

    def on_loaded(self, app):
        '''Once the app is fully loaded add API routes if required
        '''
        app.all_contents = {}
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
            if not os.path.isfile(file404):
                file404 = None
            media = MediaRouter('', path, default_suffix='html',
                                raise_404=(not file404))
            middleware.append(media)
            if file404:
                middleware.append(FileRouter('<path:path>',
                                             file404,
                                             status_code=404))

    def build(self, app):
        '''Build the static site
        '''
        config = app.config
        location = os.path.abspath(config['STATIC_LOCATION'])
        if not os.path.isdir(location):
            os.makedirs(location)
        #
        # Loop over middleware and build when instance of a Builder
        handler = app.get_handler()

        for middleware in handler.middleware:
            if isinstance(middleware, Builder):
                middleware.build(app, location)
        #
        self.copy_redirects(app, location)

    def on_html_document(self, app, request, doc):
        '''Add api Urls
        '''
        app = request.app
        jscontext = doc.jscontext
        jscontext.update(self.build_info(app))
        return
        if request.config['STATIC_API']:
            apiUrls = jscontext.get('apiUrls', {})
            for middleware in app.handler.middleware:
                if isinstance(middleware, Router):
                    middleware.add_api_urls(request, apiUrls)
            jscontext['apiUrls'] = apiUrls

    def context(self, request, context):
        if request.cache.building_static:
            # Building the static web site
            content = request.cache.content
            app = request.app
            ctx = request.cache.static_context
            if not ctx:
                if not self._global_context:
                    ctx = ContextBuilder(app)
                    self._global_context = ctx.copy()
                ctx = ContextBuilder(app, self._global_context,
                                     content=content)
                request.cache.static_context = ctx
            ctx.update(context)
            return ctx

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
                'date': dte.strftime('%Y-%m-%dT%H-%M-%S'),  # ISO 8601
                'year': dte.year,
                'lux_version': lux.__version__,
                'python_version': '.'.join((str(v) for v in
                                            sys.version_info[:3])),
                'url': url,
                'media': cfg['MEDIA_URL'][:-1],
                'name': cfg['APP_NAME']
            }
        return self._static_info.copy()

    def copy_redirects(self, app, location):
        '''Reads the ``redirects.json`` file if it exists and
        create redirects files.
        '''
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
        if isinstance(router, HtmlContent) and app.api:
            router.api = router.jsonApi()
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
