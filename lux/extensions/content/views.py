import json
import logging
import os

from pulsar import PermissionDenied, Http404
from pulsar.apps.wsgi import route, Json, Html
from pulsar.utils.slugify import slugify

from lux import forms, HtmlRouter
from lux.utils.content import get_reader
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


class TextCRUD(rest.RestMixin, HtmlRouter):
    '''CRUD views for the text APIs
    '''
    response_content_types = ('text/html', 'text/plain', 'application/json')
    uimodules = ('lux.blog',)
    content_meta = None
    '''Metadata dictionary for content routes
    '''

    def get_html(self, request):
        '''Return a div for pagination
        '''
        for slug in ('', '_'):
            try:
                return self._read(request, slug)
            except Http404:
                pass
        target = self.model.get_target(request, path='_all')
        return Html('div').attr({'blog-pagination': {'target': target}})

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
    def pagination(self, request):
        pass
        # reader = get_reader(request.app, '.%s' % self.model.ext)
        # for file in self.model.all():
        #     data = reader.process(data['content'], data['path'], slug=slug)
        # return data

    @route('<path:path>', method=('get', 'head', 'post'))
    def read_update(self, request):
        path = request.urlargs['path']
        backend = request.cache.auth_backend

        if request.method == 'GET':
            return self._read(request, path, True)

        content = self.get_model(request, path)
        if request.method == 'HEAD':
            if backend.has_permission(request, self.model.name, rest.READ):
                return request.response

        if request.method == 'POST':
            content.bla = None

        raise PermissionDenied

    def get_model(self, request, path, sha=None):
        try:
            data = self.model.read(path)
        except DataError:
            try:
                data = self.model.read(os.path.join(path, '_'))
            except DataError:
                raise Http404
        reader = get_reader(request.app, data['filename'])
        meta = self.content_meta or {}
        return reader.process(data['content'], data['path'], path, meta=meta)

    def create_model(self, request, data):
        '''Create a new document
        '''
        slug = data.get('slug') or data['title']
        data['slug'] = slugify(slug, max_length=SLUG_LENGTH)
        return self.model.write(request.cache.user, data, new=True)

    def update_model(self, request, instance, data):
        pass

    def serialise_model(self, request, data, in_list=False):
        return data

    def _read(self, request, slug='', as_response=False):
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
