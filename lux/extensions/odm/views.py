from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import load_only
from sqlalchemy import desc

from pulsar import PermissionDenied, MethodNotAllowed, Http404
from pulsar.apps.wsgi import Json

import odm

from lux import route
from lux.extensions import rest


class RestRouter(rest.RestRouter):
    '''A REST Router base on database models
    '''

    def query(self, request, session):
        odm = request.app.odm()
        model = odm[self.model.name]
        return session.query(model)

    # RestView implementation
    def get_model(self, request):
        odm = request.app.odm()
        args = request.urlargs
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


class ColumnPermissionsBase:
    def columns(self, request):
        """
        Returns column objects for this model

        :param request:     request object
        :return:            columns generator
        """
        odm = request.app.odm()
        model = odm[self.model.name]
        ins = inspect(model)
        return ins.columns

    def has_permission_for_column(self, request, column, level):
        """
        Checks permission for a column in the model

        :param request:     request object
        :param column:      column name
        :param level:       requested access level
        :return:            True iff user has permission
        """
        backend = request.cache.auth_backend
        permission_name = "{}:{}".format(self.model.name, column.name)
        return backend.has_permission(request, permission_name, level)

    def column_permissions(self, request, level):
        """
        Gets whether the user has the quested access level on
        each column in the model.

        Results are cached for future function calls

        :param request:     request object
        :param level:       access level
        :return:            dict, with column names as keys,
                            Booleans as values
        """
        ret = None
        if 'model_permissions' not in request.cache:
            request.cache.model_permissions = {}
        elif level in request.cache.model_permissions:
            ret = request.cache.model_permissions[level]
        if not ret:
            columns = self.columns(request)
            ret = {
                col.name: self.has_permission_for_column(request,
                                                         col, level) for
                col in columns
                }
            request.cache.model_permissions[level] = ret
        return ret

    def columns_with_permission(self, request, level):
        """
        Returns a frozenset with the columns the user has the requested
        level of access to

        :param request:     request object
        :param level:       access level
        :return:            frozenset of column names
        """
        perms = self.column_permissions(request, level)
        ret = frozenset(k for k, v in perms.items() if v)
        return ret

    def columns_without_permission(self, request, level):
        """
        Returns a frozenset with the columns the user does not have
        the requested level of access to

        :param request:     request object
        :param level:       access level
        :return:            frozenset of column names
        """
        perms = self.column_permissions(request, level)
        ret = frozenset(k for k, v in perms.items() if not v)
        return ret

    def check_model_permission(self, request, level):
        """
        Checks whether the user has the requested level of access to
        the model, raising PermissionDenied if not

        :param request:     request object
        :param level:       access level
        :raise:             PermissionDenied
        """
        backend = request.cache.auth_backend
        if not backend.has_permission(request, self.model.name, level):
            raise PermissionDenied


class CRUD(RestRouter, ColumnPermissionsBase):
    '''A Router for handling CRUD JSON requests for a database model
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
        return super().query(request, session).options(load_only(*entities))

    def serialise_model(self, request, data, **kw):
        """
        Makes a model instance JSON-friendly. Removes fields that the
        user does not have read access to.

        :param request:     request object
        :param data:        data
        :param kw:          not used
        :return:            dict
        """
        exclusions = self.columns_without_permission(request, rest.READ)
        return self.model.tojson(request, data, exclude=exclusions)

    def columns_for_meta(self, request):
        """
        Returns column metadata, excluding columns the user does
        not have read access to

        :param request:     request object
        :return:            dict
        """
        columns = super().columns_for_meta(request)
        allowed_columns = self.columns_with_permission(request, rest.READ)
        ret = tuple(c for c in columns if c['name'] in allowed_columns)
        return ret

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

    @route('<id>', method=('get', 'post', 'delete', 'head', 'options'))
    def read_update_delete(self, request):
        instance = self.get_model(request)

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

        elif request.method == 'POST':
            model = self.model
            form_class = model.updateform

            self.check_model_permission(request, rest.UPDATE)
            columns = self.columns_with_permission(request, rest.UPDATE)
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

        assert False
        raise MethodNotAllowed
