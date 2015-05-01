from pulsar import PermissionDenied
from pulsar.apps.wsgi import Json

from lux import route
from lux.extensions import rest


class CRUD(rest.RestRouter):

    def __init__(self, model, url=None, *args, **kwargs):
        url = url or model
        self.model = model
        super().__init__(url, *args, **kwargs)

    def collection(self, request, limit, offset, text):
        odm = request.app.odm()
        with odm.begin() as session:
            query = session.query(odm[self.model])
            data = query.limit(limit).offset(offset).all()
            return self.serialise(request, data)

    def get(self, request):
        '''Get a list of models
        '''
        backend = request.cache.auth_backend
        if backend.has_permission(request, self.model, rest.READ):
            limit = self.limit(request)
            offset = self.offset(request)
            text = self.query(request)
            data = self.collection(request, limit, offset, text)
            return Json(data).http_response(request)
        raise PermissionDenied

    def post(self, request):
        '''Create a new model
        '''
        manager = self.manager
        form_class = manager.form
        if not form_class:
            raise MethodNotAllowed
        auth = request.cache.auth_backend
        if auth and auth.has_permission(request, auth.CREATE, manager.model):
            data, files = request.data_and_files()
            form = form_class(request, data=data, files=files)
            if form.is_valid():
                instance = manager.create_model(request, form.cleaned_data)
                data = self.manager.instance_data(request, instance)
                request.response.status_code = 201
            else:
                data = form.tojson()
            return Json(data).http_response(request)
        raise PermissionDenied

    @route('<id>')
    def read(self, request):
        '''Read an instance
        '''
        odm = request.app.odm()
        instance = odm.get(request, request.urlargs['id'])
        if not instance:
            raise Http404
        url = request.absolute_uri()
        data = self.manager.instance_data(request, instance, url=url)
        return Json(data).http_response(request)

    @route('<id>')
    def post_update(self, request):
        manager = self.manager
        instance = manager.get(request, request.urlargs['id'])
        if not instance:
            raise Http404
        form_class = manager.form
        if not form_class:
            raise MethodNotAllowed
        auth = request.cache.auth_backend
        if auth.has_permission(request, auth.UPDATE, instance):
            data, files = request.data_and_files()
            form = form_class(request, data=data, files=files)
            if form.is_valid(exclude_missing=True):
                instance = manager.update_model(request, instance,
                                                form.cleaned_data)
                data = self.manager.instance(instance)
            else:
                data = form.tojson()
            return Json(data).http_response(request)
        raise PermissionDenied

    @route('delete/<id>', method='delete')
    def delete(self, request):
        manager = self.manager
        instance = manager.get(request, request.urlargs['id'])
        auth = request.cache.auth_backend
        if auth.has_permission(request, auth.DELETE, instance or self.model):
            if instance:
                manager.delete_model(request, instance)
                request.response.status_code = 204
                return request.response
            else:
                raise Http404
        raise PermissionDenied
