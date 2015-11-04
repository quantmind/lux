import lux

from pulsar import BadRequest
from pulsar.apps.wsgi import Json

from .user import READ
from .models import RestModel
from .permissions import ColumnPermissionsMixin


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


class RestMixin(ColumnPermissionsMixin):

    def __init__(self, *args, **kwargs):
        if self._model is None and args:
            model, args = args[0], args[1:]
            self.set_model(model)

        if not isinstance(self._model, RestModel):
            raise NotImplementedError('REST model not available')

        super().__init__(self._model.url, *args, **kwargs)

    def limit(self, request, default=None):
        '''The maximum number of items to return when fetching list
        of data'''
        cfg = request.config
        user = request.cache.user
        default = default or cfg['API_LIMIT_DEFAULT']
        MAXLIMIT = (cfg['API_LIMIT_AUTH'] if user.is_authenticated() else
                    cfg['API_LIMIT_NOAUTH'])
        try:
            limit = int(request.url_data.get(cfg['API_LIMIT_KEY'], default))
        except ValueError:
            limit = MAXLIMIT
        return min(limit, MAXLIMIT)

    def offset(self, request, default=None):
        '''Retrieve the offset value from the url when fetching list of data
        '''
        cfg = request.config
        default = default or 0
        try:
            return int(request.url_data.get(cfg['API_OFFSET_KEY'], default))
        except ValueError:
            return 0

    def search_text(self, request, default=None):
        cfg = request.config
        default = default or ''
        return request.url_data.get(cfg['API_SEARCH_KEY'], default)

    def serialise(self, request, data, **kw):
        if isinstance(data, list):
            kw['in_list'] = True
            return [self.serialise_model(request, o, **kw) for o in data]
        else:
            return self.serialise_model(request, data)

    def collection_response(self, request, *filters, limit=None, offset=None,
                            text=None, sortby=None, **params):
        '''Handle a response for a list of models
        '''
        app = request.app
        model = self.model(app)
        limit = self.limit(request, limit)
        offset = self.offset(request, offset)
        text = self.search_text(request, text)
        sortby = request.url_data.get('sortby', sortby)
        params.update(request.url_data)
        with model.session(request) as session:
            query = self.query(request, session, *filters)
            query = self.filter(request, query, text, params)
            total = query.count()
            query = self.sortby(request, query, sortby)
            data = query.limit(limit).offset(offset).all()
            data = self.serialise(request, data, **params)
        data = app.pagination(request, data, total, limit, offset)
        return Json(data).http_response(request)

    def query(self, request, session, *filters):
        '''Return a Query object
        '''
        raise NotImplementedError

    def filter(self, request, query, text, params, model=None):
        model = model or self.model(request.app)
        columns = model.columnsMapping(request.app)

        for key, value in params.items():
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

    def sortby(self, request, query, sortby=None):
        if sortby:
            if not isinstance(sortby, list):
                sortby = (sortby,)
            for entry in sortby:
                direction = None
                if ':' in entry:
                    entry, direction = entry.split(':')
                query = self._do_sortby(request, query, entry, direction)
        return query

    def meta(self, request):
        '''Return an object representing the metadata for the model
        served by this router
        '''
        app = request.app
        model = self.model(app)
        columns = self.columns_with_permission(request, READ)
        #
        # Don't include columns which are excluded from meta
        exclude = model._exclude
        if exclude:
            columns = [c for c in columns if c['name'] not in exclude]

        return {'id': model.id_field,
                'repr': model.repr_field,
                'columns': columns,
                'default-limit': app.config['API_LIMIT_DEFAULT']}

    def serialise_model(self, request, data, **kw):
        '''Serialise on model
        '''
        model = self.model(request.app)
        return model.tojson(request, data)

    def json_data_files(self, request):
        content_type, _ = request.content_type_options
        try:
            assert content_type == 'application/json'
            return request.data_and_files()
        except AssertionError:
            raise BadRequest('Expected application/json content type')
        except ValueError:
            raise BadRequest('Problems parsing JSON')

    def json(self, request, data):
        '''Return a response as application/json
        '''
        return Json(data).http_response(request)

    def _do_sortby(self, request, query, entry, direction):
        raise NotImplementedError

    def _do_filter(self, request, model, query, field, op, value):
        raise NotImplementedError


class RestRouter(RestMixin, lux.Router):
    response_content_types = REST_CONTENT_TYPES

    def options(self, request):
        '''Handle the CORS preflight request
        '''
        request.app.fire('on_preflight', request)
        return request.response
