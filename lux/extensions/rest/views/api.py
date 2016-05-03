from lux.core import Router

from pulsar import BadRequest
from pulsar.apps.wsgi import Json

from ..models import ModelMixin, RestModel


REST_CONTENT_TYPES = ['application/json']
DIRECTIONS = ('asc', 'desc')


class RestRoot(Router):
    '''Api Root

    Provide a get method for displaying a dictionary of api names - api urls
    key - value pairs
    '''
    response_content_types = REST_CONTENT_TYPES

    def apis(self, request):
        routes = {}
        for router in self.routes:
            url = request.absolute_uri(router.path())
            if isinstance(router, RestMixin):
                routes[router.model.api_name] = url
            else:
                routes[router.name] = url
        return routes

    def get(self, request):
        return Json(self.apis(request)).http_response(request)


class RestMixin(ModelMixin):
    '''A mixin to be used in conjunction with Routers, usually
    as the first class in the multi-inheritance declaration
    '''
    def __init__(self, *args, html=False, **kwargs):
        if self.model is None and args:
            model, args = args[0], args[1:]
            self.set_model(model)

        if not isinstance(self.model, RestModel):
            raise NotImplementedError('REST model not available')

        url = self.model.html_url if html else self.model.url
        assert url is not None, "Model %s has no valid url" % self.model
        super().__init__(url, *args, **kwargs)

    def json(self, request, data):
        '''Return a response as application/json
        '''
        return Json(data).http_response(request)

    def json_data_files(self, request):
        content_type, _ = request.content_type_options
        try:
            assert content_type == 'application/json'
            return request.data_and_files()
        except AssertionError:
            raise BadRequest('Expected application/json content type')
        except ValueError:
            raise BadRequest('Problems parsing JSON')


class RestRouter(RestMixin, Router):
    response_content_types = REST_CONTENT_TYPES

    def urlargs(self, request):
        return request.urlargs

    # RestView implementation
    def get_instance(self, request, session=None, **args):
        args = args or self.urlargs(request)
        return self.model.get_instance(request, session=session, **args)

    def options(self, request):
        '''Handle the CORS preflight request
        '''
        request.app.fire('on_preflight', request)
        return request.response
