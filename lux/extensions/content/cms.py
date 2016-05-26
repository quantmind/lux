from pulsar.utils.structures import AttributeDictionary
from pulsar.apps.wsgi import route
from pulsar.utils.httpurl import remove_double_slash
from pulsar import Http404

from lux.extensions.sitemap import Sitemap, SitemapIndex
from lux.extensions.rest import api_path
from lux.core import cached
from lux import core

from .contents import html_content


class CmsContent:
    """Model for Html Routers serving CMS content
    """
    def __init__(self, group, path=None, meta=None):
        self.group = group
        self.path = path if path is not None else group
        self.meta = meta

    def render_content(self, request, urlargs):
        path = urlargs.get('path', 'index')
        api_path = self.api_path(request, path)
        content = request.api.get(api_path).json()
        return html_content(request, content)

    def all(self, request):
        api_path = self.api_path(request)
        return request.api.get(api_path).json()['result']

    def api_path(self, request, *args):
        return api_path(request, 'contents', self.group, *args)


class TextRouter(core.HtmlRouter):
    """CRUD views for the text APIs
    """
    def __init__(self, model):
        super().__init__(model.path, model=model)

    def get_html(self, request):
        # This method is called when no other Router matched the path
        # in request. This means if no content is available will result
        # in 404 response
        request.cache.text_router = True
        return self.model.render_content(request, request.urlargs)

    @route('<path:path>')
    def read(self, request):
        return self.get(request)


class CMSmap(SitemapIndex):
    '''Build the sitemap for this Content Management System'''
    cms = None

    def items(self, request):
        for index, map in enumerate(self.cms.sitemaps):
            if not index:
                continue
            url = request.absolute_uri(str(map.route))
            _, last_modified = map.sitemap(request)
            yield AttributeDictionary(loc=url, lastmod=last_modified)


class RouterMap(Sitemap):
    model = None

    def items(self, request):
        for item in self.model.all(request):
            html_url = request.absolute_uri(item['path'])
            yield AttributeDictionary(loc=html_url,
                                      lastmod=item.get('modified'),
                                      priority=item.get('priority', 1))


class CMS(core.CMS):
    '''Override default lux :class:`.CMS` handler

    This CMS handler reads page information from the database and
    '''
    def __init__(self, app):
        super().__init__(app)
        self.sitemaps = [CMSmap('/sitemap.xml', cms=self)]
        self._middleware = []

    @classmethod
    def build(cls, app, ContentClass=None):
        cms = cls(app)
        ContentClass = ContentClass or CmsContent
        models = app.config['CONTENT_GROUPS']
        cfgs = {}
        if isinstance(models, dict):
            for name, cfg in models.items():
                if not isinstance(cfg, dict):
                    app.logger.error('content models should contain '
                                     'dictionaries')
                    continue
                if not name:
                    app.logger.error('content models should have a name')
                    continue
                path = cfg.get('path', name)
                if path == '*':
                    path = ''
                if path.startswith('/'):
                    path = path[1:]
                cfgs[path] = (name, cfg.get('meta'))

            for path in reversed(sorted(cfgs)):
                name, meta = cfgs[path]
                content = ContentClass(name, path=path, meta=meta)
                cms.add_router(content)

        app._handler.middleware.extend(cms.middleware())
        return cms

    def add_router(self, router, sitemap=True):
        if isinstance(router, CmsContent):
            router = TextRouter(router)

        if sitemap:
            path = str(router.route)
            if path != '/':
                url = remove_double_slash('%s/sitemap.xml' % path)
            else:
                url = '/sitemap1.xml'
            sitemap = RouterMap(url, model=router.model)
            self.sitemaps.append(sitemap)

        self._middleware.append(router)

    def middleware(self):
        all = self.sitemaps[:]
        all.extend(self._middleware)
        return all

    def inner_html(self, request, page, self_comp=''):
        html = super().inner_html(request, page, self_comp)
        # If this is not been already served by the Text Router check for
        # content pages
        if not request.cache.text_router:
            request.cache.html_main = html
            path = request.path[1:]
            try:
                for router in self._middleware:
                    router_args = router.resolve(path)
                    if router_args:
                        router, args = router_args
                        try:
                            html = router.model.render_content(request, args)
                        except Http404:
                            break
            finally:
                request.cache.pop('html_main')
        return html

    def context(self, request, context):
        ctx = {}
        app = request.app
        for entry in self.context_data(request):
            lazy = LazyContext(app, entry, context)
            ctx[lazy.key] = lazy
        return ctx

    @cached(key='cms:context')
    def context_data(self, request):
        return request.api.get('contents/context').json()['result']


class LazyContext:

    def __init__(self, app, entry, context):
        self.app = app
        self.key = 'html_%s' % entry['slug']
        self.entry = entry
        self.context = context

    def __str__(self):
        if not isinstance(self.context, str):
            context = self.context
            entry = self.entry
            engine = self.app.template_engine(entry.get('template_engine'))
            body = engine(entry['body'], self.context)
            template = entry.get('template')
            if template:
                context['html_main'] = body
                body = self.app.cms.render(template, context)
            self.context = body
            context[self.key] = body
        return self.context
