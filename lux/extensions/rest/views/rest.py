from pulsar import MethodNotAllowed, Http404
from pulsar.apps.wsgi import route

from lux.core import JsonRouter, GET_HEAD, Resource
from lux.forms import get_form_class, ValidationError

from ..models import RestModel


REST_CONTENT_TYPES = ['application/json']
DIRECTIONS = ('asc', 'desc')
POST_PUT_PATCH = frozenset(('POST', 'PUT', 'PATCH'))
VERBS_CHECK = frozenset(('POST', 'PUT', 'PATCH', 'DELETE', 'TRACE'))
CREATE_MODEL_ERROR_MSG = 'Could not create model'


class RestRoot(JsonRouter):
    '''Api Root

    Provide a get method for displaying a dictionary of api names - api urls
    key - value pairs
    '''
    response_content_types = REST_CONTENT_TYPES

    def apis(self, request):
        routes = {}
        for router in self.routes:
            url = '%s%s' % (request.absolute_uri('/'), router.route.rule)
            if isinstance(router, RestRouter) and router.model:
                routes[router.model.api_name] = url
            else:
                routes[router.name] = url
        return routes

    def get(self, request):
        return self.json_response(request, self.apis(request))


class Rest404(JsonRouter):
    response_content_types = REST_CONTENT_TYPES

    def get(self, request):
        raise Http404


class RestRouter(JsonRouter):
    '''A mixin to be used in conjunction with Routers, usually
    as the first class in the multi-inheritance declaration
    '''
    response_content_types = REST_CONTENT_TYPES

    def __init__(self, *args, **kwargs):
        url = None
        if args:
            url_or_model, args = args[0], args[1:]
            if isinstance(url_or_model, RestModel):
                self.model = url_or_model
            else:
                url = url_or_model

        if not self.model:
            self.model = kwargs.pop('model', None)

        if self.model:
            if url is None:
                url = self.model.identifier
            else:
                url = url.format(self.model.identifier)

        super().__init__(url, *args, **kwargs)

    def filters_params(self, request, *filters, **params):
        """Change to add positional filters and key-valued parameters
        for both the :meth:`.get_instance` and :meth:`.get_list`
        mtehods
        """
        params.update(request.urlargs)
        if 'id' in params:
            model = self.get_model(request)
            params[model.id_field] = params.pop('id')
        return filters, params

    def get_model(self, request):
        """Get the Rest model for this Router"""
        return self.model

    # RestView implementation
    def get_instance(self, request, *filters, **params):
        filters, params = self.filters_params(request, *filters, **params)
        model = self.get_model(request)
        return model.get_instance(request, *filters, **params)

    def get_list(self, request, *filters, model=None,
                 check_permission=None, **params):
        """Return a list of models satisfying user queries

        :param request: WSGI request with url data
        :param filters: positional filters passed by the application
        :param params: key-value filters passed by the application (the url
            data parameters will update this dictionary)
        :return: a pagination object as return by the
            :meth:`.query_data` method
        """
        cfg = request.config
        params.update(request.url_data)
        params['limit'] = params.pop(cfg['API_LIMIT_KEY'], None)
        params['offset'] = params.pop(cfg['API_OFFSET_KEY'], None)
        params['search'] = params.pop(cfg['API_SEARCH_KEY'], None)
        params['check_permission'] = check_permission
        if model is None:
            filters, params = self.filters_params(request, *filters, **params)
            model = self.get_model(request)
        return model.query_data(request, *filters, **params)

    def options(self, request):
        '''Handle the CORS preflight request
        '''
        verbs = [verb for verb in VERBS_CHECK if hasattr(self, verb.lower())]
        if hasattr(self, 'get'):
            verbs.extend(GET_HEAD)
        request.app.fire('on_preflight', request, methods=verbs)
        return request.response


class MetadataMixin:
    """Mixin to use with a :class:`.RestRouter` for serving
    metadata information
    """
    @route(method=('get', 'head', 'options'))
    def metadata(self, request):
        '''Model metadata'''
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=GET_HEAD)
            return request.response
        filters, params = self.filters_params(request)
        model = self.get_model(request)

        meta = model.meta(
            request,
            *filters,
            check_permission=Resource.rest(request, 'read',
                                           model.fields(),
                                           pop=1, list=True),
            **params
        )
        return self.json_response(request, meta)


class CRUD(MetadataMixin, RestRouter):
    '''A Router for handling CRUD JSON requests for a database model

    This class adds routes to the :class:`.RestRouter`
    '''
    def get(self, request):
        '''Get a list of models
        '''
        model = self.get_model(request)
        data = self.get_list(
            request,
            check_permission=Resource.rest(request, 'read',
                                           model.fields(),
                                           list=True)
        )
        return self.json_response(request, data)

    def post(self, request):
        '''Create a new model
        '''
        model = self.get_model(request)
        form_class = get_form_class(request, model.form)
        if not form_class:
            raise MethodNotAllowed

        check_permission = Resource.rest(request, 'create',
                                         model.fields(), list=True)
        fields = check_permission(request)

        instance = model.instance(fields=fields)
        data, files = request.data_and_files()
        form = form_class(request, data=data, files=files, model=model)
        if form.is_valid():
            with model.session(request) as session:
                try:
                    instance = model.create_model(request,
                                                  instance,
                                                  form.cleaned_data,
                                                  session=session)
                except ValidationError as exc:
                    form.add_error_message(str(exc) or CREATE_MODEL_ERROR_MSG)
                    data = form.tojson()
                except Exception as exc:
                    request.logger.exception(CREATE_MODEL_ERROR_MSG)
                    form.add_error_message(CREATE_MODEL_ERROR_MSG)
                    data = form.tojson()
                else:
                    data = model.tojson(request, instance)
                    request.response.status_code = 201
        else:
            data = form.tojson()

        return self.json_response(request, data)

    # Additional Routes
    @route('<id>',
           position=100,
           method=('get', 'patch', 'post', 'put', 'delete', 'head', 'options'))
    def read_update_delete(self, request):
        model = self.get_model(request)

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight',
                             request,
                             methods=model.instance_verbs())
            return request.response

        with model.session(request) as session:
            if request.method in GET_HEAD:
                instance = self.get_instance(
                    request,
                    session=session,
                    check_permission=Resource.rest(request, 'read',
                                                   model.fields())
                )
                data = model.tojson(request, instance)

            elif request.method in POST_PUT_PATCH:
                exclude_missing = False
                if request.method == 'PATCH':
                    exclude_missing = True
                    form_class = get_form_class(request, model.updateform)
                elif request.method == 'POST':
                    form_class = get_form_class(request, model.postform)
                else:
                    form_class = get_form_class(request, model.putform)

                if not form_class:
                    raise MethodNotAllowed

                instance = self.get_instance(
                    request,
                    session=session,
                    check_permission=Resource.rest(request, 'update',
                                                   model.fields())
                )
                data, files = request.data_and_files()
                form = form_class(request, data=data, files=files,
                                  previous_state=instance, model=model)

                if form.is_valid(exclude_missing=exclude_missing):
                    try:
                        instance = model.update_model(request,
                                                      instance,
                                                      form.cleaned_data,
                                                      session=session)
                    except Exception:
                        request.logger.exception('Could not update model')
                        form.add_error_message('Could not update model')
                        data = form.tojson()
                    else:
                        if isinstance(instance, dict):
                            data = instance
                        elif instance:
                            data = model.tojson(request, instance)
                        else:
                            request.response.status_code = 204
                            return request.response
                else:
                    data = form.tojson()

            elif request.method == 'DELETE':
                instance = self.get_instance(
                    request,
                    session=session,
                    check_permission=Resource.rest(request, 'delete',
                                                   model.fields())
                )
                model.delete_model(request, instance, session=session)
                request.response.status_code = 204
                return request.response

            else:
                raise MethodNotAllowed

            return self.json_response(request, data)
