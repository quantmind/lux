import os
import json
from copy import copy

import lux
from lux import route, JSON_CONTENT_TYPES
from lux.extensions import angular, base, sitemap

from pulsar import ImproperlyConfigured
from pulsar.utils.slugify import slugify
from pulsar.apps.wsgi import Json, MediaRouter, Html

from .builder import (DirBuilder, FileBuilder, BuildError, SkipBuild,
                      Unsupported, normpath)
from .contents import Article, parse_date, page_info


class ErrorRouter(lux.Router, DirBuilder):
    status_code = 500

    def get(self, request):
        app = request.app
        return app.html_response(request, self.html_body_template,
                                 status_code=self.status_code)


class HtmlRouter(angular.Router):
    '''Base class for static Html routes.
    '''
    def state_template(self, app):
        '''Template used when in html5 mode
        '''
        div = Html('div', cn=self.angular_view_class)
        div.data({'dynamic-page': ''})
        return div.render()


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
    '''Handle JSON contents in a directory
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
        # When the html router is a index template, add the index.json
        # resource for rendering the index
        if html_router.index_template:
            self.add_child(JsonIndex('index.json',
                                     dir=self.dir,
                                     index_template=html_router.index_template))
        #
        # Add Drafts API if drafts are available
        #drafts = html_router.get_route(html_router.childname('drafts'))
        #if drafts:
        #    self.add_child(JsonFile(drafts.route.rule,
        #                            dir=self.dir,
        #                            content=self.content))

        child_router = html_router.get_route(html_router.childname('view'))
        self.add_child(JsonFile('<path:id>',
                                dir=self.dir,
                                name='json_files',
                                content=self.content,
                                meta=copy(child_router.meta)))

    def get(self, request):
        '''Build all the contents
        '''
        files = self.get_route('json_files')
        data = files.all(request.app, html=False)
        return Json(data).http_response(request)


class JsonIndex(lux.Router, FileBuilder):
    index_template = None

    def build_file(self, app, location):
        src = app.template_full_path(self.index_template)
        return super(JsonIndex, self).build_file(app, location, src, 'index')

    def get(self, request):
        app = request.app
        response = request.response
        content = self.get_content(request)
        # Get the JSON representation of the resource
        data = content.json(request)
        if data:
            html_router = self.html_router
            data['api_url'] = app.site_url(self.relative_path(request))
            urlparams = content.urlparams(html_router.route.variables)
            path = html_router.path(**urlparams)
            data['html_url'] = app.site_url(normpath(path))
            return Json(data).http_response(request)
        else:
            raise Unsupported
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
            html_router = self.html_router
            urlargs = request.urlargs
            # The index page
            if urlargs.get('path') == 'index':
                urlargs['path'] = ''
            data['api_url'] = app.site_url(self.relative_path(request))
            html = html_router.get_route(html_router.childname('view'))
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
        all = []
        o = 'modified' if draft else 'date'
        for d in self.build(app):
            data = json.loads(d.body.decode('utf-8'))
            if bool(data.get('priority')=='0') is not draft:
                continue
            if not html:
                data = dict(page_info(data))
            all.append(data)
        key = lambda d: parse_date(d.get('date', d['modified']))
        return list(reversed(sorted(all, key=key)))


class HtmlFile(HtmlRouter, FileBuilder):
    '''Serve an Html file.
    '''
    def build_main(self, request, context, jscontext):
        content = self.get_content(request)
        return content.html(request, jscontext)

    def get_api_info(self, app):
        return self.parent.get_api_info(app)


class HtmlContent(HtmlRouter, DirBuilder):
    '''Serve a directory of files rendered in a similar fashion

    The directory could contains blog posts for example.
    If an ``index.html`` file is available, it is rendered with the
    directory url.
    '''
    api = None
    child_url = '<path:slug>'
    '''The relative url of files within the directory'''
    drafts = 'drafts'
    '''Drafts url. If not provided drafts wont be rendered.
    '''
    index_template = None
    meta_children = None
    drafts_template = 'blogindex.html'
    '''The children render the children routes of this router
    '''
    '''Context for the body tag'''
    priority = 1

    def __init__(self, route, *routes, **params):
        route = self.valid_route(route, params.pop('dir', None))
        name = slugify(params.pop('name', None) or route or self.dir)
        super(HtmlContent, self).__init__(route, *routes, name=name, **params)
        if self.drafts:
            self.add_child(Drafts(self.drafts,
                                  name=self.childname('drafts'),
                                  index_template=self.drafts_template))
        meta = copy(self.meta) if self.meta else {}
        if self.meta_children:
            meta.update(self.meta_children)
        #
        file = HtmlFile(self.child_url, dir=self.dir,
                        name=self.childname('view'),
                        content=self.content,
                        html_body_template=self.html_body_template,
                        meta=meta,
                        ngmodules=self.ngmodules)
        self.add_child(file)
        #
        for url_path, file_path, ext in self.all_files():
            if url_path == 'index':
                self.src = file_path
        if self.src and self.index_template:
            raise ImproperlyConfigured(
                'Both index and index template specified')

    def get_api_info(self, app):
        if self.api:
            url = app.config['SITE_URL'] + self.api.path()
            return {'name': self.api.name,
                    'url': url,
                    'type': 'static'}

    def angular_page(self, app, page):
        if self.index_template:
            url = app.config['SITE_URL'] + self.api.path()
            page['apiItems'] = {'name': self.api.name,
                                'url': '%s.json' % url,
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
                jscontext['items'] = files.all(app, html=False)
            src = app.template_full_path(self.index_template)
            content = self.read_file(app, src, 'index')
            return content.html(request, jscontext)
        elif self.src:
            content = self.read_file(request.app, self.src, 'index')
            return content.html(request, jscontext)
        else:
            raise SkipBuild


class Drafts(HtmlRouter, FileBuilder):
    '''A page collecting all drafts
    '''
    priority = 0
    ngmodules = ['lux.blog']

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
    ngmodules = ['lux.blog']


class Sitemap(sitemap.Sitemap, FileBuilder):

    def items(self, request):
        for item in self.parent.built:
            if item and item.content_type == 'text/html':
                yield item

    def build_file(self, app, location, src=None, name=None):
        router = self.parent
        assert isinstance(router, HtmlContent), ('Static sitemap requires '
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
