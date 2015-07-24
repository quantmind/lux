import json
import logging
import os

from pulsar import PermissionDenied, Http404
from pulsar.apps.wsgi import route, Json, RouterParam
from pulsar.utils.slugify import slugify

import lux
from lux import forms, HtmlRouter
from lux.extensions import rest

from .models import DataError


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


class TextCRUDBase(rest.RestMixin, HtmlRouter):
    response_content_types = ('text/html', 'text/plain', 'application/json')
    render_file = RouterParam()
    uimodules = ('lux.blog',)


class TextCRUD(TextCRUDBase):
    '''CRUD views for the text APIs
    '''
    def get_html(self, request):
        '''Return a div for pagination
        '''
        for slug in ('', '_'):
            try:
                return self.render_file(request, slug)
            except Http404:
                pass
        raise Http404

    def post(self, request):
        '''Create a new model
        '''
        form = self.model.form
        if not form:
            raise Http404
        backend = request.cache.auth_backend
        model = self.model
        if backend.has_permission(request, model.name, rest.CREATE):
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
                    data = self.serialise(request, instance)
                    request.response.status_code = 201
            else:
                data = form.tojson()
            return Json(data).http_response(request)
        raise PermissionDenied

    @route('_all', response_content_types=('application/json',))
    def all(self, request):
        return self.collection_response(request, sortby='date:desc')

    @route('_links', response_content_types=('application/json',))
    def links(self, request):
        return self.collection_response(request, sortby='order:desc')

    @route('<path:path>', method=('get', 'head', 'post'))
    def read_update(self, request):
        path = request.urlargs['path']
        backend = request.cache.auth_backend

        if request.method == 'GET':
            return self.render_file(request, path, True)

        content = self.get_model(request, path)
        if request.method == 'HEAD':
            if backend.has_permission(request, self.model.name, rest.READ):
                return request.response

        if request.method == 'POST':
            content.bla = None

        raise PermissionDenied

    def query(self, request, session):
        return session

    def get_model(self, request, path, sha=None):
        try:
            return self.model.read(request, path)
        except DataError:
            try:
                return self.model.read(request, os.path.join(path, '_'))
            except DataError:
                raise Http404

    def create_model(self, request, data):
        '''Create a new document
        '''
        slug = data.get('slug') or data['title']
        data['slug'] = slugify(slug, max_length=SLUG_LENGTH)
        return self.model.write(request.cache.user, data, new=True)

    def update_model(self, request, instance, data):
        pass

    def serialise_model(self, request, data, in_list=False, **kw):
        if in_list:
            data.pop('html', None)
            data.pop('site', None)
        return data

    def cms_html(self, request, slug, html):
        if not slug:
            slug = ('', '_')

    def render_file(self, request, slug='', as_response=False):
        content = self.get_model(request, slug)
        backend = request.cache.auth_backend

        if backend.has_permission(request, self.model.name, rest.READ):
            response = request.response
            if response.content_type == 'text/html':
                html = content.html(request)
                if as_response:
                    return self.html_response(request, html)
                else:
                    return html
            elif response.content_type == 'text/plain':
                text = content.text(request)
            else:
                text = content.json(request)
            if as_response:
                response.content = text
                return response
            else:
                return text
        raise PermissionDenied

    def _do_sortby(self, request, query, field, direction):
        return query.sortby(field, direction)

    def _do_filter(self, request, model, query, field, op, value):
        return query.filter(field, op, value)


class CMS(lux.CMS):
    '''Override default lux :class:`.CMS` handler

    This CMS handler reads page information from the database and
    '''
    def __init__(self, app):
        super().__init__(app)
        self.middleware = []

    def inner_html(self, request, page, self_comp=''):
        html = super().inner_html(request, page, self_comp)
        request.cache.html_main = html
        path = request.path[1:]

        try:
            for router in self.middleware:
                router_args = router.resolve(path)
                if router_args:
                    router, args = router_args
                    slug = None
                    if args:
                        slugs = tuple(args.values())
                    else:
                        slugs = ('', '_')
                    for slug in slugs:
                        try:
                            return router.render_file(request, slug)
                        except Http404:
                            pass

            return html
        finally:
            request.cache.pop('html_main')
