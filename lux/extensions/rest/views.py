import lux

from pulsar import BadRequest
from pulsar.apps.wsgi import Json

from .models import ModelMixin, RestModel


__all__ = ['RestRoot', 'RestRouter', 'RestMixin']


REST_CONTENT_TYPES = ['application/json']
DIRECTIONS = ('asc', 'desc')


class RestRoot(lux.Router):
    '''Api Root

    Provide a get method for displaying a dictionary of api names - api urls
    key - value pairs
    '''
    response_content_types = REST_CONTENT_TYPES

    def apis(self, request):
        routes = {}
        app = request.app
        for router in self.routes:
            model = router.model(app)
            routes[model.api_name] = request.absolute_uri(router.path())
        return routes

    def get(self, request):
        return Json(self.apis(request)).http_response(request)


class RestMixin(ModelMixin):

    def __init__(self, *args, **kwargs):
        if self._model is None and args:
            model, args = args[0], args[1:]
            self.set_model(model)

        if not isinstance(self._model, RestModel):
            raise NotImplementedError('REST model not available')

        super().__init__(self._model.url, *args, **kwargs)

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


class RestRouter(RestMixin, lux.Router):
    response_content_types = REST_CONTENT_TYPES

    def options(self, request):
        '''Handle the CORS preflight request
        '''
        request.app.fire('on_preflight', request)
        return request.response
