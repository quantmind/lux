from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import load_only
from sqlalchemy import desc

from pulsar import PermissionDenied, MethodNotAllowed, Http404
from pulsar.apps.wsgi import Json

import odm

from lux import route
from lux.extensions import rest


class RestRouter(rest.RestRouter):
    '''A REST Router based on database models
    '''
    def query(self, request, session):
        """
        Returns a query object for the model.

        The loading of columns the user does not have read
        access to is deferred. This is only a performance enhancement.

        :param request:     request object
        :param session:     SQLAlchemy session
        :return:            query object
        """
        entities = self.columns_with_permission(request, rest.READ)
        if not entities:
            raise PermissionDenied
        model = self.model.db_model()
        db_columns = self.model.db_columns(self.column_fields(entities))
        return session.query(model).options(load_only(*db_columns))

    # RestView implementation
    def get_model(self, request, **args):
        odm = request.app.odm()
        args = args or request.urlargs
        if not args:  # pragma    nocover
            raise Http404
        with odm.begin() as session:
            query = self.query(request, session)
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
                self.set_model_attribute(instance, name, value)
        return instance

    def update_model(self, request, instance, data):
        odm = request.app.odm()
        with odm.begin() as session:
            session.add(instance)
            for name, value in data.items():
                self.set_model_attribute(instance, name, value)
        return instance

    def delete_model(self, request, instance):
        with request.app.odm().begin() as session:
            session.delete(instance)

    def set_model_attribute(self, instance, name, value):
        '''Set the the attribute ``name`` to ``value`` in a model ``instance``
        '''
        current_value = getattr(instance, name, None)
        if isinstance(current_value, list):
            if not isinstance(value, (list, tuple)):
                raise TypeError('list or tuple required')
            current_value[:] = value
        else:
            setattr(instance, name, value)

    def serialise_model(self, request, data, **kw):
        """
        Makes a model instance JSON-friendly. Removes fields that the
        user does not have read access to.

        :param request:     request object
        :param data:        data
        :param kw:          not used
        :return:            dict
        """
        exclude = self.columns_without_permission(request, rest.READ)
        exclude = self.column_fields(exclude, 'name')
        return self.model.tojson(request, data, exclude=exclude)

    def meta(self, request):
        meta = super().meta(request)
        odm = request.app.odm()
        model = odm[self.model.name]
        with odm.begin() as session:
            query = session.query(model)
            meta['total'] = query.count()
        return meta

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

    def _do_sortby(self, request, query, entry, direction):
        if direction == 'desc':
            entry = desc(entry)
        return query.order_by(entry)


class CRUD(RestRouter):
    '''A Router for handling CRUD JSON requests for a database model

    This class adds routes to the :class:`.RestRouter`
    '''
    def get(self, request):
        '''Get a list of models
        '''
        self.check_model_permission(request, rest.READ)
        # Columns the user doesn't have access to are dropped by
        # serialise_model
        return self.collection_response(request)

    def post(self, request):
        '''Create a new model
        '''
        model = self.model
        assert model.form

        self.check_model_permission(request, rest.CREATE)
        columns = self.columns_with_permission(request, rest.CREATE)
        columns = self.column_fields(columns)

        data, files = request.data_and_files()
        form = model.form(request, data=data, files=files)
        if form.is_valid():
            # At the moment, we silently drop any data
            # for columns the user doesn't have update access to,
            # like they don't exist
            filtered_data = {k: v for k, v in form.cleaned_data.items() if
                             k in columns}
            try:
                instance = self.create_model(request, filtered_data)
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

    @route('<id>', method=('get', 'post', 'put', 'delete', 'head', 'options'))
    def read_update_delete(self, request):
        args = {self.model.id_field: request.urlargs['id']}
        instance = self.get_model(request, **args)

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        elif request.method == 'GET':
            self.check_model_permission(request, rest.READ)
            # url = request.absolute_uri()
            # Columns the user doesn't have access to are dropped by
            # serialise_model
            data = self.serialise(request, instance)
            return Json(data).http_response(request)

        elif request.method == 'HEAD':
            self.check_model_permission(request, rest.READ)
            return request.response

        elif request.method in ('POST', 'PUT'):
            model = self.model
            form_class = model.updateform

            self.check_model_permission(request, rest.UPDATE)
            columns = self.columns_with_permission(request, rest.UPDATE)
            columns = self.column_fields(columns)

            if not form_class:
                raise MethodNotAllowed

            data, files = request.data_and_files()
            form = form_class(request, data=data, files=files,
                              previous_state=instance)
            if form.is_valid(exclude_missing=True):
                # At the moment, we silently drop any data
                # for columns the user doesn't have update access to,
                # like they don't exist
                filtered_data = {k: v for k, v in form.cleaned_data.items()
                                 if k in columns}

                instance = self.update_model(request, instance,
                                             filtered_data)
                data = self.serialise(request, instance)
            else:
                data = form.tojson()
            return Json(data).http_response(request)

        elif request.method == 'DELETE':

            self.check_model_permission(request, rest.DELETE)
            self.delete_model(request, instance)
            request.response.status_code = 204
            return request.response

        raise MethodNotAllowed
