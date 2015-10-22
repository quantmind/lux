from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import load_only
from sqlalchemy import desc

from pulsar import PermissionDenied, MethodNotAllowed, Http404
from pulsar.apps.wsgi import Json

import odm

from lux import route
from lux.extensions import rest

from .models import RestModel


class RestRouter(rest.RestRouter):
    '''A REST Router based on database models
    '''
    RestModel = RestModel

    def urlargs(self, request):
        return request.urlargs

    def query(self, request, session, *filters):
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
        model = self.model(request.app)
        db_model = model.db_model()
        db_columns = model.db_columns(self.column_fields(entities))
        query = session.query(db_model).options(load_only(*db_columns))
        if filters:
            query = query.filter(*filters)
        return model.query(query)

    # RestView implementation
    def get_instance(self, request, session=None, **args):
        odm = request.app.odm()
        args = args or self.urlargs(request)
        if not args:  # pragma    nocover
            raise Http404
        with odm.begin(session=session) as session:
            query = self.query(request, session)
            try:
                return query.filter_by(**args).one()
            except (DataError, NoResultFound):
                raise Http404

    def create_model(self, request, data):
        odm = request.app.odm()
        model = self.model(request.app)
        db_model = model.db_model()
        with odm.begin() as session:
            instance = db_model()
            session.add(instance)
            for name, value in data.items():
                model.set_model_attribute(instance, name, value)
        with odm.begin() as session:
            session.add(instance)
            # we need to access the related fields in order to avoid
            # session not bound
            model.load_related(instance)
        return instance

    def update_model(self, request, instance, data):
        model = self.model(request)
        odm = request.app.odm()
        session = odm.session_from_object(instance)
        with odm.begin(session=session) as session:
            session.add(instance)
            for name, value in data.items():
                model.set_model_attribute(instance, name, value)
        return instance

    def delete_model(self, request, instance):
        odm = request.app.odm()
        session = odm.session_from_object(instance)
        with odm.begin(session=session) as session:
            session.delete(instance)

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
        model = self.model(request.app)
        return model.tojson(request, data, exclude=exclude)

    def meta(self, request):
        meta = super().meta(request)
        odm = request.app.odm()
        with odm.begin() as session:
            query = self.query(request, session)
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
    def urlargs(self, request):
        model = self.model(request)
        return {model.id_field: request.urlargs['id']}

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
        model = self.model(request.app)
        if not model.form:
            raise MethodNotAllowed

        self.check_model_permission(request, rest.CREATE)
        columns = self.columns_with_permission(request, rest.CREATE)
        columns = self.column_fields(columns, 'name')

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
        model = self.model(request.app)

        if backend.has_permission(request, model.name, rest.READ):
            meta = self.meta(request)
            return Json(meta).http_response(request)
        raise PermissionDenied

    @route('<id>', method=('get', 'post', 'put', 'delete', 'head', 'options'))
    def read_update_delete(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        model = self.model(request.app)
        odm = request.app.odm()
        with odm.begin() as session:
            instance = self.get_instance(request, session)

            if request.method == 'GET':
                self.check_model_permission(request, rest.READ)
                data = self.serialise(request, instance)

            elif request.method == 'HEAD':
                self.check_model_permission(request, rest.READ)
                return request.response

            elif request.method in ('POST', 'PUT'):
                form_class = model.updateform

                if not form_class:
                    raise MethodNotAllowed

                self.check_model_permission(request, rest.UPDATE)
                columns = self.columns_with_permission(request, rest.UPDATE)
                columns = self.column_fields(columns, 'name')

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

            elif request.method == 'DELETE':

                self.check_model_permission(request, rest.DELETE)
                self.delete_model(request, instance)
                request.response.status_code = 204
                return request.response

            else:
                raise MethodNotAllowed

            return Json(data).http_response(request)
