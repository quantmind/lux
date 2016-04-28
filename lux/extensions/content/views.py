import json
import logging

from pulsar import PermissionDenied, Http404, MethodNotAllowed
from pulsar.apps.wsgi import route, Json
from pulsar.utils.httpurl import remove_double_slash

from lux import forms
from lux.extensions import rest

from .utils import get_context_files, get_reader, get_content, DataError


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


class SnippetCRUD(rest.RestRouter):

    def get(self, request):
        ctx = {}
        for key in get_context_files(request.app):
            ctx[key] = request.absolute_uri(key)
        return self.json(request, ctx)

    @route('<key>', method=('get', 'options'))
    def _context_path(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['GET'])
            return request.response
        ctx = get_context_files(request.app)
        src = ctx.get(request.urlargs['key'])
        if not src:
            raise Http404
        app = request.app
        content = get_reader(app, src).read(src)
        return self.json(request, content.json(app))


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
    def _links(self, request):
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
