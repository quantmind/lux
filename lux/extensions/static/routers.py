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


class File(html5.Router, FileBuilder):

    def get(self, request):
        snippet = self.get_snippet(request)
        if snippet.content_type == 'text/html':
            return super(File, self).get(request)
        else:
            response = request.response
            response.content_type = snippet.content_type
            response.content = snippet._content
            return response


class JsonFile(lux.Router, FileBuilder):
    response_content_types = lux.RouterParam(JSON_CONTENT_TYPES)

    def get(self, request):
        response = request.response
        snipped = self.get_snippet(request)
        context = request.app.context(request)
        json = snipped.json(context)
        if json:
            response.content = snipped.json(context)
            return response

    def should_build(self, app, path=None, **params):
        if app.config['STATIC_HTML5']:
            return path not in app.config['STATIC_SPECIALS']
        return False


class JsonRoot(lux.Router, FileBuilder):
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
    response_content_types = lux.RouterParam(JSON_CONTENT_TYPES)

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


class HtmlContent(html5.Router, DirBuilder):
    '''Serve a directory of files rendered in a similar fashion

    If not specified, the ``route`` value is used
    '''
    def __init__(self, route, dir=None, name=None):
        route = self.valid_route(route, dir)
        name = slugify(name or route or self.dir)
        route = '%s/' % route
        file = File('<path:path>', dir=self.dir)
        super(HtmlContent, self).__init__(route, file, name=name)
        #
        for url_path, file_path, ext in self.all_files():
            if url_path == 'index':
                self.src = file_path

    def add_api_urls(self, request, api):
        name = self.get_api_name()
        route = self.get_route('json_resource')
        if name and route:
            path = route.path(path='')
            api[name] = path
            for route in self.routes:
                route.add_api_urls(request, api)

    def get_api_name(self):
        return slugify(self.get_src(), separator='_')


class Blog(HtmlContent):
    '''Defaults for a blog url
    '''
    children = Article
