import os
import json

import lux
from lux import route, JSON_CONTENT_TYPES
from lux.extensions import html5, base

from pulsar.utils.slugify import slugify
from pulsar.apps.wsgi import Json, MediaRouter

from .builder import (DirBuilder, FileBuilder, BuildError, SkipBuild,
                      HttpException)
from .contents import Article, Draft, parse_date


SPECIAL_KEYS = ('html_url',)


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
        for route in self.routes:
            path = request.absolute_uri(route.path())
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
        route = self.valid_route(route, dir)[:-1] or self.dir
        name = slugify(name or route or self.dir)
        self.src = '%s.json' % self.dir
        assert html_router, 'html router required'
        super(JsonContent, self).__init__(route, name=name,
                                          html_router=html_router,
                                          content=html_router.content,
                                          template=html_router.template)
        self.add_child(JsonFile('<id>',
                                dir=self.dir,
                                name='json_files',
                                content=self.content,
                                template=html_router.template))

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
        context = request.app.context(request)
        data = content.json_dict(app, context)
        if data:
            urlargs = request.urlargs
            if urlargs.get('path') == 'index':
                urlargs['path'] = ''
            data['api_url'] = app.site_url(request, request.path)
            html = self.html_router.get_route('html_files')
            urlparams = content.context(app, names=html.route.variables)
            path = html.path(**urlparams)
            data['html_url'] = app.site_url(request, path)
            return Json(data).http_response(request)
        else:
            raise HttpException
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
            data = json.loads(d.decode('utf-8'))
            if bool(data['draft']) is not draft:
                continue
            if not html:
                data = dict(((key, data[key]) for key in data
                             if not self.is_html(key)))
            all.append(data)
        return list(reversed(sorted(all, key=lambda d: parse_date(d[o]))))

    def is_html(self, key):
        return key.startswith('html_') and key not in SPECIAL_KEYS


class HtmlFile(html5.Router, FileBuilder):
    '''Serve an Html file
    '''
    def build_main(self, request, context, jscontext):
        content = self.get_content(request)
        if content.content_type == 'text/html':
            # First build the global context
            context = request.app.context(request, context)
            # update the global context with context from this file
            return content.html(request, context)
        else:
            raise HttpException

    def get_api_info(self, app):
        return self.parent.get_api_info(app)


class Partial(html5.Router, FileBuilder):
    '''Serve an Html file
    '''
    def get(self, request):
        content = self.get_content(request)
        request.response.content_type = content.content_type
        request.response.content = content._content
        return request.response


class HtmlContent(html5.Router, DirBuilder):
    '''Serve a directory of files rendered in a similar fashion

    The directory could contains blog posts for example.
    If an ``index.html`` file is available, it is rendered with the
    directory url

    If not specified, the ``route`` value is used
    '''
    index_template = None
    api = None
    full = True
    '''If true render templates as full html5 pages'''
    drafts = 'drafts'
    '''Drafts url
    '''
    drafts_template = 'blogindex.html'
    '''The children render the children routes of this router
    '''

    def __init__(self, route, *routes, dir=None, name=None, **params):
        route = self.valid_route(route, dir)
        name = slugify(name or route or self.dir)
        super(HtmlContent, self).__init__(route, *routes, name=name, **params)
        if self.drafts:
            self.add_child(Drafts(self.drafts,
                                  index_template=self.drafts_template))
        if self.full:
            file = HtmlFile(self.child_url, dir=self.dir, name='html_files',
                            content=self.content, archive=self.archive,
                            html_body_template=self.html_body_template,
                            template=self.template)
        else:
            file = Partial(self.child_url, dir=self.dir, name='html_files',
                           content=self.content)
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
            raise SkipBuild
        if self.index_template:
            app = request.app
            files = self.api.get_route('json_files') if self.api else None
            if files:
                jscontext['dir_entries'] = files.all(app, html=False)
            return app.render_template(self.index_template, context)
        # Not building, render the source file
        elif self.src:
            content = self.read_file(request.app, self.src, 'index')
            context = request.app.context(request, context)
            return content.html(request, context)
        else:
            raise SkipBuild


class Drafts(html5.Router, FileBuilder):
    '''A page collecting all drafts
    '''
    def build_main(self, request, context, jscontext):
        if self.index_template and self.parent:
            app = request.app
            api = self.parent.api
            files = api.get_route('json_files') if api else None
            if files:
                jscontext['dir_entries'] = files.all(app, html=False,
                                                     draft=True)
            return app.render_template(self.index_template, context)
        else:
            raise SkipBuild


class Blog(HtmlContent):
    '''Defaults for a blog url
    '''
    index_template = 'blogindex.html'
    content = Article
