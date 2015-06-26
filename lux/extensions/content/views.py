import logging

from pulsar import PermissionDenied, Http404
from pulsar.apps.wsgi import route, Json
from pulsar.utils.slugify import slugify

from lux import forms, HtmlRouter
from lux.extensions import rest
from lux.extensions.static import get_reader

from .models import DataError


SLUG_LENGTH = 64
logger = logging.getLogger('lux.extensions.content')


class TextForm(forms.Form):
    title = forms.CharField()
    slug = forms.CharField(required=False,
                           max_length=SLUG_LENGTH)
    author = forms.CharField(required=False)
    body = forms.TextField()
    tags = forms.CharField(required=False)
    published = forms.DateTimeField(required=False)


class TextCRUD(rest.RestMixin, HtmlRouter):
    '''CRUD views for the text APIs
    '''
    response_content_types = ('text/html', 'text/plain', 'application/json')

    def get(self, request):
        '''Return a list of contents
        '''
        return request.response

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

    @route('<slug>', method=('get', 'head', 'post'))
    def read_update(self, request):
        content = self.get_model(request, request.urlargs['slug'])
        backend = request.cache.auth_backend

        if request.method == 'GET':
            if backend.has_permission(request, self.model.name, rest.READ):
                if request.content_types.best == 'text/html':
                    html = content.html(request)
                    return self.html_response(request, html)
                elif request.content_types.best == 'text/plain':
                    return content
                else:
                    return content

        elif request.method == 'HEAD':
            if backend.has_permission(request, self.model.name, rest.READ):
                return request.response

    def get_model(self, request, slug, sha=None):
        try:
            data = self.model.read(slug)
        except DataError:
            raise Http404
        reader = get_reader(request.app, '.%s' % self.model.ext)
        return reader.process(data['content'], data['path'], slug=slug)

    def create_model(self, request, data):
        '''Create a new document
        '''
        slug = data.get('slug') or data['title']
        data['slug'] = slugify(slug, max_length=SLUG_LENGTH)
        data['hash'] = self.model.write(request.cache.user, data, new=True)
        return data

    def update_model(self, request, instance, data):
        pass

    def serialise_model(self, request, data, in_list=False):
        return data
