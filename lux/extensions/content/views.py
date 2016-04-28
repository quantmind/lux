import json
import logging

from pulsar import PermissionDenied, Http404, MethodNotAllowed
from pulsar.apps.wsgi import route, Json, RouterParam
from pulsar.utils.structures import AttributeDictionary
from pulsar.utils.httpurl import remove_double_slash

from lux import core, forms
from lux.extensions import rest
from lux.extensions.sitemap import Sitemap, SitemapIndex
from lux.core.content import html as get_html

from .models import Content, DataError


SLUG_LENGTH = 64
logger = logging.getLogger('lux.extensions.content')


class TextForm(forms.Form):
    title = forms.CharField()
    slug = forms.CharField(required=False,
                           max_length=SLUG_LENGTH)
    author = forms.CharField(required=False)
    body = forms.TextField(text_edit=json.dumps({'mode': 'markdown'}))
    tags = forms.CharField(required=False)
    published = forms.DateTimeField(required=False)


def list_filter(model, filters):
    filters['path:ne'] = remove_double_slash('/%s' % model.html_url)
    return filters


class ContentCRUD(rest.RestRouter):

    def get(self, request):
        self.check_model_permission(request, 'read')
        filters = list_filter(self.model, {})
        return self.model.collection_response(request, sortby='date:desc',
                                              **filters)

    def post(self, request):
        '''Create a new model
        '''
        model = self.model
        if not model.form:
            raise Http404
        backend = request.cache.auth_backend
        if backend.has_permission(request, model.name, 'create'):
            data, files = self.json_data_files(request)
            form = model.form(request, data=data, files=files)
            if form.is_valid():
                try:
                    instance = self.create_model(request, form.cleaned_data)
                except DataError as exc:
                    logger.exception('Could not create model')
                    form.add_error_message(str(exc))
                    data = form.tojson()
                else:
                    data = model.serialise(request, instance)
                    request.response.status_code = 201
            else:
                data = form.tojson()
            return Json(data).http_response(request)
        raise PermissionDenied

    @route('_links', method=('get', 'options'))
    def links(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['GET'])
            return request.response
        filters = list_filter(self.model, {'order:gt': 0})
        return self.model.collection_response(
            request, sortby=['title:asc', 'order:desc'], **filters)

    @route('<path:path>', method=('get', 'head', 'post', 'options'))
    def read_update(self, request):
        path = request.urlargs['path']
        model = self.model

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        content = get_content(request, model, path)

        if request.method == 'GET':
            self.check_model_permission(request, 'read', content)
            data = model.serialise(request, content)
            if data == request.response:
                return data

        elif request.method == 'HEAD':
            self.check_model_permission(request, 'read', content)
            return request.response

        else:
            raise MethodNotAllowed

        return self.json(request, data)


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
        for item in model.all(request):
            item = item.json(request)
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


def get_content(request, model, path):
    app = request.app
    if app.rest_api_client:
        api = app.api(request)
        return api.get('%s/%s' % (model.url, path)).json()
    else:
        try:
            return model.get_instance(request, path)
        except DataError:
            raise Http404


def render_content(request, model, urlargs):
    path = urlargs.get('path', 'index')
    content = get_content(request, model, path)
    return get_html(request, content)
