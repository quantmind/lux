from pulsar.utils.structures import AttributeDictionary
from pulsar.apps.wsgi import route, RouterParam
from pulsar.utils.httpurl import remove_double_slash
from pulsar import Http404

from lux.extensions.sitemap import Sitemap, SitemapIndex
from lux.core.content import html as get_html
from lux.extensions import rest
from lux import core

from .models import Content
from .utils import get_content, get_context


def render_content(request, model, urlargs):
    path = urlargs.get('path', 'index')
    content = get_content(request, model, path)
    return get_html(request, content)


class TextRouterBase(rest.RestMixin, core.HtmlRouter):
    model = RouterParam()


class TextRouter(TextRouterBase):
    """CRUD views for the text APIs
    """
    def get_html(self, request):
        request.cache.text_router = True
        return render_content(request, self.model, request.urlargs)

    @route('<path:path>')
    def read(self, request):
        return self.get(request)


class TextCMS(TextRouter):
    '''A Text CRUD Router which can be used as CMS Router
    '''
    def response_wrapper(self, callable, request):
        try:
            return callable(request)
        except Http404:
            pass


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

    def add_router(self, router, sitemap=True):
        if isinstance(router, Content):
            router = TextCMS(router, html=True)
        router.model = self.app.models.register(router.model)

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
        if not request.cache.text_router:
            request.cache.html_main = html
            path = request.path[1:]
            try:
                for router in self._middleware:
                    router_args = router.resolve(path)
                    if router_args:
                        router, args = router_args
                        try:
                            html = render_content(request, router.model, args)
                        except Http404:
                            pass
            finally:
                request.cache.pop('html_main')
        return html

    def context(self, request, context):
        return get_context(request, context)
