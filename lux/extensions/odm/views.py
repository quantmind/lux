from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc

from pulsar import PermissionDenied, MethodNotAllowed, Http404
from pulsar.apps.wsgi import Json

import odm

from lux import route
from lux.extensions import rest


DIRECTIONS = ('asc', 'desc')


class RestRouter(rest.RestRouter):
    '''A REST Router base on database models
    '''
    # RestView implementation
    def collection(self, request, limit, offset, text):
        app = request.app
        odm = app.odm()
        model = odm[self.model.name]

        with odm.begin() as session:
            query = session.query(model)
            query = self.filter(request, query, text)
            total = query.count()
            query = self.sortby(request, query)
            data = query.limit(limit).offset(offset).all()
            data = self.serialise(request, data)
            return app.pagination(request, data, total, limit, offset)

    def get_model(self, request):
        odm = request.app.odm()
        model = odm[self.model.name]
        args = request.urlargs
        if not args:    # pragma    nocover
            raise Http404
        with odm.begin() as session:
            query = session.query(model)
            try:
                return query.filter_by(**args).one()
            except (DataError, NoResultFound):
                raise Http404

    def create_model(self, request, data):
        odm = request.app.odm()
        model = odm[self.model.name]
        with odm.begin() as session:
            instance = model(**data)
            session.add(instance)
        return instance

    def update_model(self, request, instance, data):
        odm = request.app.odm()
        with odm.begin() as session:
            for key, value in data.items():
                setattr(instance, key, value)
            session.add(instance)
        return instance

    def meta(self, request):
        meta = super().meta(request)
        odm = request.app.odm()
        model = odm[self.model.name]
        with odm.begin() as session:
            query = session.query(model)
            meta['total'] = query.count()
        return meta

    def sortby(self, request, query):
        sortby = request.url_data.get('sortby')
        if sortby:
            if not isinstance(sortby, list):
                sortby = (sortby,)
            for entry in sortby:
                direction = None
                if ':' in entry:
                    entry, direction = entry.split(':')
                if direction not in DIRECTIONS:
                    direction = DIRECTIONS[0]
                if direction == 'desc':
                    entry = desc(entry)
                query = query.order_by(entry)
        return query

    def filter(self, request, query, text):
        filterby = request.url_data.get('filterby')
        if filterby:
            if not isinstance(filterby, list):
                filterby = (filterby,)
            for entry in filterby:
                bits = entry.split(':')
                if len(bits) == 3:
                    query = self._do_filter(query, *bits)
        return query

    def _do_filter(self, query, field, op, value):
        if op == 'eq':
            query = query.filter_by(**{field: value})
        return query


class CRUD(RestRouter):

    def get(self, request):
        '''Get a list of models
        '''
        backend = request.cache.auth_backend
        model = self.model
        if backend.has_permission(request, model.name, rest.READ):
            limit = self.limit(request)
            offset = self.offset(request)
            text = self.query(request)
            data = self.collection(request, limit, offset, text)
            return Json(data).http_response(request)
        raise PermissionDenied

    @route(method=('get', 'options'))
    def metadata(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        backend = request.cache.auth_backend
        model = self.model
        if backend.has_permission(request, model.name, rest.READ):
            meta = self.meta(request)
            return Json(meta).http_response(request)
        raise PermissionDenied

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
                    odm.logger.exception('Could not create model')
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
        # url = request.absolute_uri()
        data = self.serialise(request, instance)
        return Json(data).http_response(request)

    @route('<id>')
    def post_update(self, request):
        model = self.model
        instance = self.get_model(request)
        form_class = model.editform or model.form
        if not form_class:
            raise MethodNotAllowed

        backend = request.cache.auth_backend
        if backend.has_permission(request, model.name, rest.UPDATE):
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
        instance = self.get_model(request)
        backend = request.cache.auth_backend
        if backend.has_permission(request, self.model.name, rest.DELETE):
            with request.app.odm().begin() as session:
                session.delete(instance)
            request.response.status_code = 204
            return request.response
        raise PermissionDenied
