from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound

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

    # RestView implementation
    def get_instance(self, request, session=None, **args):
        odm = request.app.odm()
        args = args or self.urlargs(request)
        if not args:  # pragma    nocover
            raise Http404
        model = self.model(request)
        with odm.begin(session=session) as session:
            query = model.query(request, session)
            try:
                return query.filter_by(**args).one()
            except (DataError, NoResultFound):
                raise Http404


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
        self.check_model_permission(request, 'read')
        # Columns the user doesn't have access to are dropped by
        # serialise_model
        return self.model(request).collection_response(request)

    def post(self, request):
        '''Create a new model
        '''
        model = self.model(request.app)
        if not model.form:
            raise MethodNotAllowed

        self.check_model_permission(request, 'create')
        columns = model.columns_with_permission(request, 'create')
        columns = model.column_fields(columns, 'name')

        data, files = request.data_and_files()
        form = model.form(request, data=data, files=files)
        if form.is_valid():
            # At the moment, we silently drop any data
            # for columns the user doesn't have update access to,
            # like they don't exist
            filtered_data = {k: v for k, v in form.cleaned_data.items() if
                             k in columns}
            with model.session(request) as session:
                try:
                    instance = model.create_model(request, filtered_data,
                                                  session=session)
                except DataError as exc:
                    odm.logger.exception('Could not create model')
                    form.add_error_message(str(exc))
                    data = form.tojson()
                else:
                    data = model.serialise(request, instance)
                    request.response.status_code = 201
        else:
            data = form.tojson()
        return Json(data).http_response(request)

    # Additional Routes

    @route(method=('get', 'options'))
    def metadata(self, request):
        '''Model metadata
        '''
        backend = request.cache.auth_backend
        model = self.model(request.app)
        if backend.has_permission(request, model.name, 'read'):
            if request.method == 'OPTIONS':
                request.app.fire('on_preflight', request)
                return request.response

            meta = model.meta(request)
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
            instance = self.get_instance(request, session=session)

            if request.method == 'GET':
                self.check_model_permission(request, 'read')
                data = model.serialise(request, instance)

            elif request.method == 'HEAD':
                self.check_model_permission(request, 'read')
                return request.response

            elif request.method in ('POST', 'PUT'):
                form_class = model.updateform

                if not form_class:
                    raise MethodNotAllowed

                self.check_model_permission(request, 'update')
                columns = model.columns_with_permission(request, 'update')
                columns = model.column_fields(columns, 'name')

                data, files = request.data_and_files()
                form = form_class(request, data=data, files=files,
                                  previous_state=instance)
                if form.is_valid(exclude_missing=True):
                    # At the moment, we silently drop any data
                    # for columns the user doesn't have update access to,
                    # like they don't exist
                    filtered_data = {k: v for k, v in form.cleaned_data.items()
                                     if k in columns}

                    instance = model.update_model(request, instance,
                                                  filtered_data)
                    data = model.serialise(request, instance)
                else:
                    data = form.tojson()

            elif request.method == 'DELETE':

                self.check_model_permission(request, 'delete')
                model.delete_model(request, instance)
                request.response.status_code = 204
                return request.response

            else:
                raise MethodNotAllowed

            return Json(data).http_response(request)
