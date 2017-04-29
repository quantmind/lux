from pulsar.api import Http404

from lux.core import JsonRouter
from lux.models import Model


REST_CONTENT_TYPES = ['application/json']
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
                routes[router.model.uri] = url
            else:
                routes[router.name] = url
        return routes

    def get(self, request):
        return request.json_response(self.apis(request))


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
            if isinstance(url_or_model, Model):
                self.model = url_or_model
            else:
                url = url_or_model

        if not self.model:
            self.model = kwargs.pop('model', None)

        if self.model:
            if url is None:
                url = self.model.uri
            else:
                url = url.format(self.model.uri)

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
