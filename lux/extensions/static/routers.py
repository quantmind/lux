import os
import json
from copy import copy

import lux
from lux import route, JSON_CONTENT_TYPES
from lux.extensions import angular, base, sitemap

from pulsar.utils.slugify import slugify
from pulsar.apps.wsgi import Json, MediaRouter

from .builder import (DirBuilder, FileBuilder, BuildError, SkipBuild,
                      Unsupported, normpath)
from .contents import Article, parse_date


SPECIAL_KEYS = ('html_url',)
SKIP_KEYS = ('site', 'head')


class ErrorRouter(lux.Router, DirBuilder):
    status_code = 500

    def get(self, request):
        app = request.app
        return app.html_response(request, self.html_body_template,
                                 status_code=self.status_code)


class MediaBuilder(base.MediaRouter, FileBuilder):

    def build(self, app, location=None):
        '''Build the files for this Builder
        '''
        if location is None:
            location = os.path.abspath(app.config['STATIC_LOCATION'])
        if self.built is not None:
            return self.built
        self.built = []
        for url_base, src in self.extension_paths(app):
            for upath, src, ext in self.all_files(src):
                url = '%s.%s' % (os.path.join(url_base, upath), ext)
                self.build_file(app, location, src=src, name=url)


class JsonRedirect(lux.Router):

    def __init__(self, route):
        route = str(route)
        if route.startswith('/'):
            route = route[1:]
        self.target = '/%s' % route
        if route.endswith('/'):
            route = route[:-1]
        assert route, 'JSON route not defined'
        super(JsonRedirect, self).__init__('/%s.json' % route)

    def get(self, request):
        return request.redirect(self.target)


class JsonRoot(lux.Router, FileBuilder):
    '''The root for :class:`.JsonContent`
    '''
    response_content_types = lux.RouterParam(JSON_CONTENT_TYPES)

    def apis(self, request):
        routes = {}
        site_url = request.config['SITE_URL']
        for route in self.routes:
            path = route.path()
            if site_url:
                path = '%s%s' % (site_url, path)
            url = '%s.json' % path
            routes['%s_url' % route.name] = url
        return routes

    def get(self, request):
        return Json(self.apis(request)).http_response(request)


class JsonContent(lux.Router, DirBuilder):
    '''Handle json contents in a directory
    '''
    html_router = lux.RouterParam(None)

    def __init__(self, route, dir=None, name=None, html_router=None):
        route = self.valid_route(route, dir)[:-1]
        base = os.path.basename(self.dir)
        route = route or base
        name = slugify(name or route)
        self.src = '%s.json' % route
        assert html_router, 'html router required'
        super(JsonContent, self).__init__(route, name=name,
                                          html_router=html_router,
                                          content=html_router.content,
                                          meta=copy(html_router.meta))
        child_router = html_router.get_route('html_files')
        self.add_child(JsonFile('<id>',
                                dir=self.dir,
                                name='json_files',
                                content=self.content,
                                meta=copy(child_router.meta)))

    def get(self, request):
        '''Build all the contents'''
        files = self.get_route('json_files')
        data = files.all(request.app, html=False)
        return Json(data).http_response(request)


class JsonFile(lux.Router, FileBuilder):
    '''Serve/build a json file
    '''
    def get(self, request):
        app = request.app
        response = request.response
        content = self.get_content(request)
        # Get the JSON representation of the resource
        data = content.json(request)
        if data:
            urlargs = request.urlargs
            if urlargs.get('path') == 'index':
                urlargs['path'] = ''
            data['api_url'] = app.site_url(self.relative_path(request))
            html = self.html_router.get_route('html_files')
            urlparams = content.urlparams(html.route.variables)
            path = html.path(**urlparams)
            data['html_url'] = app.site_url(normpath(path))
            return Json(data).http_response(request)
        else:
            raise Unsupported
        return Json(data).http_response(request)

    def should_build(self, app, name):
        '''Don't build json api for special contents (404 for example)
        '''
        return name not in app.config['STATIC_SPECIALS']

    def all(self, app, html=True, draft=False):
        contents = self.build(app)
        all = []
        o = 'modified' if draft else 'date'
        for d in self.build(app):
            data = json.loads(d.body.decode('utf-8'))
            if bool(data.get('priority')=='0') is not draft:
                continue
            if not html:
                data = dict(((key, data[key]) for key in data
                             if not self.is_html(key)))
            all.append(data)
        key = lambda d: parse_date(d.get('date', d['modified']))
        return list(reversed(sorted(all, key=key)))

    def is_html(self, key):
        if key not in SPECIAL_KEYS:
            return key.startswith('html_') or key in SKIP_KEYS


class HtmlFile(angular.Router, FileBuilder):
    '''Serve an Html file.
    '''
    def build_main(self, request, context, jscontext):
        content = self.get_content(request)
        return content.html(request)

    def get_api_info(self, app):
        return self.parent.get_api_info(app)


class HtmlContent(angular.Router, DirBuilder):
    '''Serve a directory of files rendered in a similar fashion

    The directory could contains blog posts for example.
    If an ``index.html`` file is available, it is rendered with the
    directory url.
    '''
    index_template = None
    api = None
    drafts = 'drafts'
    '''Drafts url. If not provided drafts wont be rendered.
    '''
    drafts_template = 'blogindex.html'
    '''The children render the children routes of this router
    '''
    '''Context for the body tag'''
    priority = 1

    def __init__(self, route, *routes, dir=None, name=None,
                 meta_children=None, **params):
        route = self.valid_route(route, dir)
        name = slugify(name or route or self.dir)
        super(HtmlContent, self).__init__(route, *routes, name=name, **params)
        if self.drafts:
            self.add_child(Drafts(self.drafts,
                                  index_template=self.drafts_template))
        meta = copy(self.meta)
        if meta_children:
            meta.update(meta_children)
        #
        file = HtmlFile(self.child_url, dir=self.dir, name='html_files',
                        content=self.content,
                        html_body_template=self.html_body_template,
                        meta=meta,
                        ngmodules=self.ngmodules)
        self.add_child(file)
        #
        for url_path, file_path, ext in self.all_files():
            if url_path == 'index':
                self.src = file_path

    def get_api_info(self, app):
        if self.api:
            url = app.config['SITE_URL'] + self.api.path()
            return {'name': self.api.name,
                    'url': url,
                    'urlparams': {'path': 'index.json'},
                    'type': 'static'}

    def build_main(self, request, context, jscontext):
        '''Build the ``main`` key for the ``context`` dictionary
        '''
        if self.src and request.cache.building_static:
            raise SkipBuild     # it will be built by the file handler
        if self.index_template:
            # Don't use the content and the template if given
            self.content = None
            if self.meta:
                self.meta.pop('template', None)
            app = request.app
            files = self.api.get_route('json_files') if self.api else None
            if files:
                jscontext['posts'] = files.all(app, html=False)
            src = app.template_full_path(self.index_template)
            content = self.read_file(app, src, 'index')
            return content.html(request)
        elif self.src:
            content = self.read_file(request.app, self.src, 'index')
            return content.html(request)
        else:
            raise SkipBuild


class Drafts(angular.Router, FileBuilder):
    '''A page collecting all drafts
    '''
    priority = 0
    ngmodules = ['blog']

    def build_main(self, request, context, jscontext):
        if self.index_template and self.parent:
            app = request.app
            api = self.parent.api
            doc = request.html_document
            doc.head.replace_meta('robots', 'noindex, nofollow')
            files = api.get_route('json_files') if api else None
            if files:
                jscontext['posts'] = files.all(app, html=False, draft=True)
            return app.render_template(self.index_template, context)
        else:
            raise SkipBuild


class Blog(HtmlContent):
    '''Defaults for a blog url
    '''
    index_template = 'blogindex.html'
    content = Article
    ngmodules = ['blog']


class Sitemap(sitemap.Sitemap, FileBuilder):

    def items(self, request):
        for item in self.parent.built:
            if item and item.content_type == 'text/html':
                yield item

    def build_file(self, app, location, src=None, name=None):
        router = self.parent
        assert isinstance(router, HtmlContent), ('Staticsitemap requires '
                                                 'HtmlContent')
        router.build_done(self._build_file)
        self.built.append(None)

    def _build_file(self, app, location, build):
        path = self.route.path
        request = app.wsgi_request(path=path, HTTP_ACCEPT='*/*')
        response = self.response(request.environ, {})
        #
        dst_filename = os.path.join(location, path[1:])
        dirname = os.path.dirname(dst_filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        app.logger.info('Creating "%s"', dst_filename)
        with open(dst_filename, 'wb') as f:
            f.write(response.content[0])
