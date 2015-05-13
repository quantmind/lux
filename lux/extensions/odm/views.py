from sqlalchemy.exc import DataError

from pulsar import PermissionDenied
from pulsar.apps.wsgi import Json

from lux import route
from lux.extensions import rest

from .serialise import tojson
from .mapper import logger


class CRUD(rest.RestRouter):
    addform = None
    editform = None

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
        backend = request.cache.auth_backend
        if backend.has_permission(request, self.model, rest.CREATE):
            assert self.addform
            data, files = request.data_and_files()
            form = self.addform(request, data=data, files=files)
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

    @route('<id>')
    def read(self, request):
        '''Read an instance
        '''
        instance = self.get_model(request)
        url = request.absolute_uri()
        data = self.serialise(request, instance)
        return Json(data).http_response(request)

    @route('<id>')
    def post_update(self, request):
        instance = self.get_model(request)
        form_class = self.editform or self.addform
        if not form_class:
            raise MethodNotAllowed

        backend = request.cache.auth_backend
        if backend.has_permission(request, self.model, rest.UPDATE):
            data, files = request.data_and_files()
            form = form_class(request, data=data, files=files)
            if form.is_valid(exclude_missing=True):
                instance = self.update_model(request, instance,
                                             form.cleaned_data)
                data = self.serialise(request, instance)
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

    def get_model(self, request):
        odm = request.app.odm()
        with odm.begin() as session:
            query = session.query(odm[self.model])
            try:
                return query.get(request.urlargs['id'])
            except NoResultFound:
                raise Http404

    def create_model(self, request, data):
        odm = request.app.odm()
        model = odm[self.model]
        with odm.begin() as session:
            instance = model(**data)
            session.add(instance)
        return instance

    def update_model(self, request, instance, data):
        odm = request.app.odm()
        model = odm[self.model]
        with odm.begin() as session:
            for key, value in data.items():
                setattr(instance, key, value)
            session.add(instance)
        return instance

    def serialise_model(self, request, data, in_list=False):
        return tojson(data)
