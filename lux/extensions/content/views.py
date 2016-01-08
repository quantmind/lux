import json
import logging

from pulsar import PermissionDenied, Http404, HttpRedirect
from pulsar.apps.wsgi import route, Json, RouterParam
from pulsar.utils.slugify import slugify
from pulsar.utils.structures import AttributeDictionary
from pulsar.utils.httpurl import remove_double_slash

import lux
from lux import forms, HtmlRouter
from lux.extensions import rest
from lux.extensions.sitemap import Sitemap, SitemapIndex

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


class ContentCRUD(rest.RestRouter):

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

    @route('<path:path>', method=('get', 'head', 'post'))
    def read_update(self, request):
        path = request.urlargs['path']
        model = self.model(request.app)
        backend = request.cache.auth_backend

        if request.method == 'GET':
            try:
                return self.render_file(request, path, True)
            except Http404:
                if not path.endswith('/'):
                    if model.exist(request, '%s/index' % path):
                        raise HttpRedirect('%s/' % path)
                raise

        content = get_content(request, model, path)
        if request.method == 'HEAD':
            if backend.has_permission(request, model.name, 'read'):
                return request.response

        if request.method == 'POST':
            content.bla = None


class TextRouterBase(rest.RestMixin, HtmlRouter):
    render_file = RouterParam()


class TextRouter(TextRouterBase):
    '''CRUD views for the text APIs
    '''
    def get_html(self, request):
        '''Return a div for pagination
        '''
        return self.render_file(request, 'index')

    @route('_all', response_content_types=('application/json',))
    def all(self, request):
        return self.model.collection_response(request, sortby='date:desc')

    @route('_links', response_content_types=('application/json',))
    def links(self, request):
        return self.model.collection_response(
            request, sortby=['order:desc', 'title:asc'], **{'order:gt': 0})

    @route('<path:path>')
    def read(self, request):
        path = request.urlargs['path']
        try:
            return self.render_file(request, path, True)
        except Http404:
            if not path.endswith('/'):
                if model.exist(request, '%s/index' % path):
                    raise HttpRedirect('%s/' % path)
            raise

    def render_file(self, request, path='', as_response=False):
        if path.endswith('/'):
            path = '%sindex' % path
        model = self.model
        backend = request.cache.auth_backend

        if backend.has_permission(request, model.name, 'read'):
            content = get_content(request, model, path)
            response = request.response
            response.content_type = content.content_type
            if content.content_type == 'text/html':
                #
                # Update with context from this router
                content._meta.update(self.context(request) or ())

                if response.content_type == 'application/json':
                    data = content.json(request)
                    if as_response:
                        return Json(data).http_response(request)
                    else:
                        return data
                else:
                    html = content.html(request)
                    if as_response:
                        return self.html_response(request, html)
                    else:
                        return html
            elif as_response:
                response.content_type = content.content_type
                response.content = content.raw(request)
                return response
            else:
                return content.raw(request)

        raise PermissionDenied


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
        model = self.content_router.model(request)
        for item in model.all(request):
            yield AttributeDictionary(loc=item['url'],
                                      lastmod=item['modified'],
                                      priority=item['priority'])


class CMS(lux.CMS):
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
        request.cache.html_main = html
        path = request.path[1:]

        try:
            for router in self._middleware:
                router_args = router.resolve(path)
                if router_args:
                    router, args = router_args
                    path = tuple(args.values())[0] if args else 'index'
                    try:
                        return router.render_file(request, path)
                    except Http404:
                        return html

            return html
        finally:
            request.cache.pop('html_main')


def get_content(request, model, path):
    try:
        return model.read(request, path)
    except DataError:
        raise Http404
