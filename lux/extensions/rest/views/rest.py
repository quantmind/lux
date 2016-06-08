from pulsar import BadRequest, PermissionDenied
from pulsar.apps.wsgi import route

from lux.core import JsonRouter

from ..models import ModelMixin, RestModel


REST_CONTENT_TYPES = ['application/json']
DIRECTIONS = ('asc', 'desc')


class RestRoot(JsonRouter):
    '''Api Root

    Provide a get method for displaying a dictionary of api names - api urls
    key - value pairs
    '''
    response_content_types = REST_CONTENT_TYPES

    def apis(self, request):
        routes = {}
        for router in self.routes:
            url = '%s%s' % (request.absolute_uri(), router.route.rule)
            if isinstance(router, RestRouter):
                routes[router.model.api_name] = url
            else:
                routes[router.name] = url
        return routes

    def get(self, request):
        return self.json_response(request, self.apis(request))


class RestRouter(ModelMixin, JsonRouter):
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

        if not isinstance(self.model, RestModel):
            raise TypeError('REST model not available in %s router' %
                            self.__class__.__name__)

        url = url or self.model.url
        assert url is not None, "Model %s has no valid url" % self.model
        super().__init__(url, *args, **kwargs)

    def json_data_files(self, request):
        content_type, _ = request.content_type_options
        try:
            assert content_type == 'application/json'
            return request.data_and_files()
        except AssertionError:
            raise BadRequest('Expected application/json content type')
        except ValueError:
            raise BadRequest('Problems parsing JSON')

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


class MetadataMixin:
    """Mixin to use with a :class:`.RestRouter` for serving
    metadata information
    """

    @route(method=('get', 'head', 'options'))
    def metadata(self, request):
        '''Model metadata
        '''
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['GET', 'HEAD'])
            return request.response

        backend = request.cache.auth_backend
        model = self.model
        if backend.has_permission(request, model.name, 'read'):
            meta = model.meta(request)
            return self.json_response(request, meta)

        raise PermissionDenied
