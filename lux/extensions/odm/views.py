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
            instance = model()
            session.add(instance)
            for name, value in data.items():
                self.set_instance_value(instance, name, value)
        return instance

    def update_model(self, request, instance, data):
        odm = request.app.odm()
        with odm.begin() as session:
            session.add(instance)
            for name, value in data.items():
                self.set_instance_value(instance, name, value)
        return instance

    def delete_model(self, request, instance):
        with request.app.odm().begin() as session:
            session.delete(instance)

    def set_instance_value(self, instance, name, value):
        setattr(instance, name, value)

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

    def filter(self, request, query, text, model=None):
        model = model or self.model
        columns = model.columnsMapping(request.app)

        for key, value in request.url_data.items():
            bits = key.split(':')
            field = bits[0]
            if field in columns:
                col = columns[field]
                op = bits[1] if len(bits) == 2 else 'eq'
                field = col.get('field')
                if field:
                    query = self._do_filter(request, model, query,
                                            field, op, value)
        return query

    def _do_filter(self, request, model, query, field, op, value):
        if value == '':
            value = None
        odm = request.app.odm()
        field = getattr(odm[model.name], field)
        if op == 'eq':
            query = query.filter(field == value)
        elif op == 'gt':
            query = query.filter(field > value)
        elif op == 'ge':
            query = query.filter(field >= value)
        elif op == 'lt':
            query = query.filter(field < value)
        elif op == 'le':
            query = query.filter(field <= value)
        return query


class CRUD(RestRouter):
    '''A Router for handling CRUD JSON requests for a database model
    '''
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

    # Additional Routes

    @route(method=('get', 'options'))
    def metadata(self, request):
        '''Model metadata
        '''
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        backend = request.cache.auth_backend
        model = self.model
        if backend.has_permission(request, model.name, rest.READ):
            meta = self.meta(request)
            return Json(meta).http_response(request)
        raise PermissionDenied

    @route('<id>', method=('get', 'post', 'delete', 'head', 'options'))
    def read_update_delete(self, request):
        instance = self.get_model(request)
        backend = request.cache.auth_backend

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        elif request.method == 'GET':
            # url = request.absolute_uri()
            data = self.serialise(request, instance)
            return Json(data).http_response(request)

        elif request.method == 'HEAD':
            return request.response

        elif request.method == 'POST':
            model = self.model
            form_class = model.updateform
            if not form_class:
                raise MethodNotAllowed

            if backend.has_permission(request, model.name, rest.UPDATE):
                data, files = request.data_and_files()
                form = form_class(request, data=data, files=files,
                                  previous_state=instance)
                if form.is_valid(exclude_missing=True):
                    instance = self.update_model(request, instance,
                                                 form.cleaned_data)
                    data = self.serialise(request, instance)
                else:
                    data = form.tojson()
                return Json(data).http_response(request)

        elif request.method == 'DELETE':

            if backend.has_permission(request, self.model.name, rest.DELETE):
                self.delete_model(request, instance)
                request.response.status_code = 204
                return request.response

        raise PermissionDenied
