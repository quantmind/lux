from pulsar.utils.structures import AttributeDictionary
from pulsar.apps.wsgi import route
from pulsar.utils.httpurl import remove_double_slash
from pulsar import Http404

from lux.extensions.sitemap import Sitemap, SitemapIndex
from lux.core.content import html as get_html
from lux.core import cached
from lux import core


class CmsContent:
    """Model for Html Routers serving CMS content
    """
    def __init__(self, group, path=None, meta=None, api=None):
        self.group = group
        self.path = path if path is not None else group
        self.meta = meta
        self.api = api or 'contents'

    def render_content(self, request, urlargs):
        path = urlargs.get('path', 'index')
        api_path = self.api_path(request, path)
        content = request.api.get(api_path).json()
        return get_html(request, content)

    def api_path(self, request, path):
        return '%s/%s/%s' % (self.api, self.group, path)


class TextRouter(core.HtmlRouter):
    """CRUD views for the text APIs
    """
    def __init__(self, model):
        super().__init__(model.path, model=model)

    def get_html(self, request):
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
    content_router = None

    def items(self, request):
        model = self.content_router.model
        # TODO: this need to be generalised to api
        for item in model.all(request):
            item = model.serialise_model(request, item)
            yield AttributeDictionary(loc=item['html_url'],
                                      lastmod=item['modified'],
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
        models = app.config['CONTENT_MODELS']
        if isinstance(models, list):
            for cfg in models:
                if not isinstance(cfg, dict):
                    app.logger.error('content models should contain '
                                     'dictionaries')
                    continue
                name = cfg.get('name')
                if not name:
                    app.logger.error('content models should have a name')
                    continue
                path = cfg.get('path', name)
                content = ContentClass(name, path=path, meta=cfg.get('meta'))
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
            sitemap = RouterMap(url, content_router=router)
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
                            pass
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
