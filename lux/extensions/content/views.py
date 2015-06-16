import logging

from pulsar import PermissionDenied
from pulsar.apps.wsgi import route, Json
from pulsar.utils.slugify import slugify

from lux import forms
from lux.extensions import rest

from .models import Content, DataError


SLUG_LENGTH = 64
logger = logging.getLogger('lux.extensions.content')


class BlogForm(forms.Form):
    title = forms.CharField()
    slug = forms.CharField(required=False,
                           max_length=SLUG_LENGTH)
    author = forms.CharField()
    body = forms.TextField()
    tags = forms.CharField(required=False)
    published = forms.DateTimeField(required=False)


class TextCRUD(rest.RestRouter):
    '''CRUD views for the text APIs
    '''
    def __init__(self, name, path, *args, **kwargs):
        model = Content(name, path, form=BlogForm)
        super().__init__(model, *args, **kwargs)

    def post(self, request):
        '''Create a new model
        '''
        backend = request.cache.auth_backend
        model = self.model
        if backend.has_permission(request, model.name, rest.CREATE):
            assert model.form
            data, files = request.data_and_files()
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

    @route('id')
    def update(self, request):
        backend = request.cache.auth_backend
        model = self.model
        if backend.has_permission(request, model.name, rest.CREATE):
            assert model.form
            data, files = request.data_and_files()
            form = model.form(request, data=data, files=files)
            if form.is_valid():
                pass

    def create_model(self, request, data):
        '''Create a new document
        '''
        slug = data.get('slug') or data['title']
        data['slug'] = slugify(slug, max_length=SLUG_LENGTH)
        self.model.write(request.cache.user, data, new=True)

    def get_model(self, request, slug, sha=None):
        pass

    def update_model(self, request, instance, data):
        pass
