'''
Include Sphinx json files into a static website
'''
import os

from pulsar import ImproperlyConfigured

from ..routers import JsonContent, JsonFile, HtmlContent, HtmlFile, normpath
from ..contents import Content
try:
    from .builder import LuxSphinx
except ImportError:
    LuxSphinx = None


class SphinxContent(Content):

    def __init__(self, app, meta, ctx):
        meta.update(ctx.get('meta', ()))
        meta['content_type'] = 'text/html'
        content = ctx.get('body', '')
        super(SphinxContent, self).__init__(app, content, meta,
                                            ctx.get('src'), ctx['pagename'])


class SphinxMixin(object):

    def get_content(self, request):
        content = request.cache.content
        if not content:
            raise NotImplementedError('Not implemented yet')
        return content

    def build(self, app, location=None):
        '''Build the files for this Builder
        '''
        if self.built is not None:
            return self.built
        if location is None:
            location = os.path.abspath(app.config['STATIC_LOCATION'])
        data = getattr(self.html_router, '_doc_build', None)
        if data is None:
            data = self.build_sphinx(app, location)
            self.html_router._doc_build = data
        self.built = []
        for ctx in data:
            self.build_file(app, location, ctx)
        return self.built

    def build_file(self, app, location, ctx):
        urlparams = {self.route.ordered_variables[0]: ctx['pagename']}
        path = self.path(**urlparams)
        url = app.site_url(normpath(path))
        content = SphinxContent(app, self.meta.copy(), ctx)
        request = app.wsgi_request(path=url, extra={'HTTP_ACCEPT': '*/*'})
        request.cache.building_static = True
        request.cache.content = content
        response = self.response(request.environ, urlparams)
        self.write(app, request, location, response)

    def build_sphinx(self, app, location):
        if not LuxSphinx:
            raise ImproperlyConfigured('Sphinx not installed')
        path = self.html_router.path()[1:]
        if path:
            location = os.path.join(location, path)
        if not os.path.isdir(location):
            os.makedirs(location)
        srcdir = os.path.abspath(self.dir)
        doctreedir = os.path.join(location, '_doctrees')
        app = LuxSphinx(app, srcdir, srcdir, location, doctreedir, 'lux')
        force_all = False
        app.build(force_all)
        return app.data


class SphinxFiles(SphinxMixin, HtmlFile):
    pass


class SphinxJsonFiles(SphinxMixin, JsonFile):
    pass


class SphinxJsonDocs(JsonContent):
    JsonFileRouter = SphinxJsonFiles


class SphinxDocs(HtmlContent):
    JsonApiRouter = SphinxJsonDocs
    HtmlFileRouter = SphinxFiles
    drafts = None
