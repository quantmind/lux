import os
import json

import lux
from lux import route, JSON_CONTENT_TYPES
from lux.extensions import html5, base

from pulsar.utils.slugify import slugify
from pulsar.apps.wsgi import Json

from .builder import DirBuilder, FileBuilder, BuildError
from .contents import Article


class ErrorRouter(lux.Router, DirBuilder):
    status_code = 500

    def get(self, request):
        app = request.app
        return app.html_response(request, self.html_body_template,
                                 status_code=self.status_code)


class MediaRouter(base.MediaRouter, FileBuilder):

    def build(self, app, location=None):
        '''Build the files for this Builder
        '''
        if location is None:
            location = os.path.abspath(app.config['STATIC_LOCATION'])
        if self.built is not None:
            return self.built
        self.built = []
        for url_base, src in self.extension_paths(app):
            for upath, fpath, ext in self.all_files(src):
                url = '%s.%s' % (os.path.join(url_base, upath), ext)
                self.build_file(app, location, ext, path=url)


class JsonFile(lux.Router, FileBuilder):
    response_content_types = lux.RouterParam(JSON_CONTENT_TYPES)

    def get(self, request):
        response = request.response
        snipped = self.get_snippet(request)
        context = request.app.context(request)
        data = snipped.json_dict(context)
        if data:
            #data['api_url'] = request.path
            return Json(data).http_response(request)

    def should_build(self, app, path=None, **params):
        return path not in app.config['STATIC_SPECIALS']


class JsonRoot(lux.Router, FileBuilder):
    '''The root for :class:`.JsonContent`
    '''
    response_content_types = lux.RouterParam(JSON_CONTENT_TYPES)

    def apis(self, request):
        routes = {}
        for route in self.routes:
            url = '%s.json' % request.absolute_uri(route.path())
            routes['%s_url' % route.name] = url
        return routes

    def get(self, request):
        return Json(self.apis(request)).http_response(request)


class JsonContent(lux.Router, DirBuilder):
    '''Handle json content in a directory
    '''
    def __init__(self, route, dir=None, name=None):
        route = self.valid_route(route, dir) or self.dir
        name = slugify(name or route or self.dir)
        self.src = '%s.json' % self.dir
        files = JsonFile('<path:path>', dir=self.dir, name='json_files')
        super(JsonContent, self).__init__(route, files, name=name)

    def get(self, request):
        '''Build all the contents'''
        files = self.get_route('json_files')
        contents = files.build(request.app)
        data = [json.loads(d.decode('utf-8')) for d in contents]
        return Json(data).http_response(request)


class HtmlFile(html5.Router, FileBuilder):
    '''Serve an Html file
    '''
    def build_main(self, request):
        snippet = self.get_snippet(request)
        context = request.app.context(request)
        return snippet.html(request, context)

    def get_api_info(self, app):
        return self.parent.get_api_info(app)


class HtmlContent(html5.Router, DirBuilder):
    '''Serve a directory of files rendered in a similar fashion

    If not specified, the ``route`` value is used
    '''
    template = None
    api = None

    def __init__(self, route, *routes, dir=None, name=None, **params):
        route = self.valid_route(route, dir)
        name = slugify(name or route or self.dir)
        route = '%s/' % route
        file = HtmlFile('<path:path>', dir=self.dir)
        routes = list(routes)
        routes.append(file)
        super(HtmlContent, self).__init__(route, *routes, name=name, **params)
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


class Blog(HtmlContent):
    '''Defaults for a blog url
    '''
    children = Article
