import os

import lux
from lux import route, JSON_CONTENT_TYPES
from lux.extensions import html5, base

from .builder import StaticBuilder, BuildError
from .contents import Article


class ErrorRouter(lux.Router, StaticBuilder):
    status_code = 500

    def get(self, request):
        app = request.app
        return app.html_response(request, self.html_body_template,
                                 status_code=self.status_code)


class MediaRouter(base.MediaRouter, StaticBuilder):

    def build(self, app, location):
        '''Build the files for this Builder
        '''
        for url_base, src in self.extension_paths(app):
            for upath, fpath, ext in self.all_files(src):
                url = '%s.%s' % (os.path.join(url_base, upath), ext)
                self.build_file(app, location, ext, path=url)


class Content(html5.Router, StaticBuilder):
    pass


class JsonContent(lux.Router, StaticBuilder):
    '''Handle json content when using HTML5 navigation
    '''
    response_content_types = lux.RouterParam(JSON_CONTENT_TYPES)

    def get(self, request):
        response = request.response
        path = request.urlargs['path']
        dir = self.parent.dir
        if dir:
            path = os.path.join(dir, path)
        try:
            snipped = self.read_file(request.app, path)
        except BuildError:
            _, name = os.path.split(path)
            if name == 'index' and self.index_template:
                src = self.template_full_path(self.index_template)
                snipped = self.read_file(request.app, src)
            else:
                raise
        context = request.app.context(request)
        response.content = snipped.json(context)
        return response

    def should_build(self, app, path=None, **params):
        if app.config['STATIC_HTML5']:
            return path not in app.config['STATIC_SPECIALS']
        return False


class DirContent(html5.Router, StaticBuilder):
    '''Serve a directory of files rendered in a similar fashion

    If not specified, the ``route`` value is used
    '''
    def __init__(self, route, *routes, **kwargs):
        if not route.endswith('/'):
            route = '%s/' % route
        # We need to build these here rather than in the body of the class
        # so that they are served before the input *routes
        api = JsonContent('_json/<path:path>')
        #partial = Partial('_partial', name='partial_template')
        content = Content('<path:path>')
        super(DirContent, self).__init__(route, api, content, *routes,
                                         **kwargs)


class Blog(DirContent):
    '''Defaults for a blog url
    '''
    create_routes = False
    children = Article
