import json
import logging
from copy import copy

from pulsar import PermissionDenied
from pulsar.utils.html import nicename
from pulsar.apps.wsgi import Json

from .user import READ, PERMISSION_LEVELS

PERMISSIONS = ['UPDATE', 'CREATE', 'DELETE']

logger = logging.getLogger('lux.extensions.rest')

__all__ = ['RestModel', 'RestColumn', 'ModelMixin']


class RestColumn:
    '''A class for specifying attributes of a REST column/field
    for a model
    '''

    def __init__(self, name, sortable=None, filter=None, type=None,
                 displayName=None, field=None, hidden=None):
        self.name = name
        self.sortable = sortable
        self.filter = filter
        self.type = type
        self.displayName = displayName
        self.field = field
        self.hidden = hidden

    @classmethod
    def make(cls, col):
        if isinstance(col, RestColumn):
            return col
        assert isinstance(col, str), 'Not a string'
        return cls(col)

    def __repr__(self):  # pragma    nocover
        return self.name

    __str__ = __repr__

    def as_dict(self, defaults=True):
        return dict(self._as_dict(defaults))

    def _as_dict(self, defaults):
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue
            if v is None and defaults:
                if k == 'displayName':
                    v = nicename(self.name)
                elif k == 'field':
                    v = self.name
                elif k == 'type':
                    v = 'string'
            if v is not None:
                yield k, v


class ColumnPermissionsMixin:
    '''Mixin for managing model permissions at column (field) level

    This mixin can be used by any class.
    '''
    def column_fields(self, columns, field=None):
        '''Return a list column fields from the list of columns object
        '''
        field = field or 'field'
        fields = set()
        for c in columns:
            value = c[field]
            if isinstance(value, (tuple, list)):
                fields.update(value)
            else:
                fields.add(value)
        return tuple(fields)

    def has_permission_for_column(self, request, column, level):
        """
        Checks permission for a column in the model

        :param request:     request object
        :param column:      column name
        :param level:       requested access level
        :return:            True iff user has permission
        """
        backend = request.cache.auth_backend
        permission_name = "{}:{}".format(self.name, column['name'])
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
        cache = request.cache
        if 'model_permissions' not in cache:
            cache.model_permissions = {}
        if self.name not in cache.model_permissions:
            cache.model_permissions[self.name] = {}
        elif level in cache.model_permissions[self.name]:
            ret = cache.model_permissions[self.name][level]

        if not ret:
            perm = self.has_permission_for_column
            columns = self.columns(request)
            ret = {
                col['name']: perm(request, col, level) for
                col in columns
                }
            cache.model_permissions[self.name][level] = ret
        return ret

    def columns_with_permission(self, request, level):
        """
        Returns a frozenset with the columns the user has the requested
        level of access to

        :param request:     request object
        :param level:       access level
        :return:            frozenset of column names
        """
        columns = self.columns(request)
        perms = self.column_permissions(request, level)
        return tuple((col for col in columns if perms.get(col['name'])))

    def columns_without_permission(self, request, level):
        """
        Returns a frozenset with the columns the user does not have
        the requested level of access to

        :param request:     request object
        :param level:       access level
        :return:            frozenset of column names
        """
        columns = self.columns(request)
        perms = self.column_permissions(request, level)
        return tuple((col for col in columns if not perms.get(col['name'])))


class RestModel(ColumnPermissionsMixin):
    '''Hold information about a model used for REST views

    .. attribute:: name

        name of this REST model

    .. attribute:: api_name

        name used as key in the dictionary of API endpoints. By default it is
        given by the plural of name + `_url`

    .. attribute:: form

        Form class for this REST model

    .. attribute:: updateform

        Form class for this REST model in editing mode. If not provided
        no editing is allowed.

    .. attribute:: exclude

        Optional list of column names to exclude from the json
        representation of a model instance

    .. attribute:: hidden

        Optional list of column names which will have the hidden attribute
        set to True in the :class:`.RestColumn` metadata
    '''
    remote_options_str = 'item.id as item.name for item in {options}'
    remote_options_str_ui_select = 'item.id as item in {options}'
    _app = None
    _loaded = False
    _col_mapping = None

    def __init__(self, name, form=None, updateform=None, columns=None,
                 url=None, api_name=None, exclude=None,
                 api_url=None, html_url=None, id_field=None,
                 repr_field=None, hidden=None):
        assert name, 'model name not available'
        self.name = name
        self.form = form
        self.updateform = updateform
        self.url = url if url is not None else '%ss' % name
        self.api_name = '%s_url' % (self.url or self.name)
        self.id_field = id_field or 'id'
        self.repr_field = repr_field or 'id'
        self._api_url = api_url
        self._html_url = html_url
        self._columns = columns
        self._exclude = set(exclude or ())
        self._hidden = set(hidden or ())

    def __repr__(self):
        return self.name

    __str__ = __repr__

    def set_model_attribute(self, instance, name, value):
        '''Set the the attribute ``name`` to ``value`` in a model ``instance``
        '''
        setattr(instance, name, value)

    def tojson(self, request, object, exclude=None, decoder=None):
        '''Convert a model ``object`` into a JSON serializable
        dictionary
        '''
        raise NotImplementedError

    def session(self, request):
        '''Return a session for aggregating a query.
        The retunred object should be context manager and support the query
        method.
        '''
        raise NotImplementedError

    def query(self, request, session, *filters):
        '''Manipulate a query if needed
        '''
        raise NotImplementedError

    def columns(self, request):
        '''Return a list fields describing the entries for a given model
        instance'''
        if not self._loaded:
            self._columns = self._load_columns(request.app)
            self._loaded = True
        return self._columns

    def columnsMapping(self, request):
        '''Returns a dictionary of names/columns objects
        '''
        if self._col_mapping is None:
            self._col_mapping = dict(((c['name'], c) for c in
                                      self.columns(request)))
        return self._col_mapping

    def get_target(self, request, **extra_data):
        '''Get a target for a form

        Used by HTML Router to get information about the LUX REST API
        of this Rest Model
        '''
        url = self._api_url or request.app.config.get('API_URL')
        if not url:
            return
        target = {'url': url, 'name': self.api_name}
        target.update(**extra_data)
        return target

    def field_options(self, request):
        '''Return a generator of options for a html serializer
        '''
        if not request:
            logger.error('%s cannot get remote target. No request', self)
        else:
            target = self.get_target(request)
            yield 'data-remote-options', json.dumps(target)
            yield 'data-remote-options-id', self.id_field
            yield 'data-remote-options-value', json.dumps({
                'type': 'field',
                'source': self.repr_field})
            yield 'data-ng-options', self.remote_options_str.format(
                options=self.api_name)
            yield 'data-ng-options-ui-select', \
                self.remote_options_str_ui_select.format(options=self.api_name)

    def limit(self, request, limit=None, max_limit=None):
        '''The maximum number of items to return when fetching list
        of data'''
        cfg = request.config
        user = request.cache.user
        if not max_limit:
            max_limit = (cfg['API_LIMIT_AUTH'] if user.is_authenticated() else
                         cfg['API_LIMIT_NOAUTH'])
        max_limit = int(max_limit)
        default = cfg['API_LIMIT_DEFAULT']
        try:
            limit = int(limit)
            if limit <= 0:
                limit = default
        except Exception:
            limit = default
        return min(limit, max_limit)

    def offset(self, request, offset=None):
        '''Retrieve the offset value from the url when fetching list of data
        '''
        try:
            offset = int(offset)
        except Exception:
            offset = 0
        return max(0, offset)

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

    def collection_response(self, request, *filters, **params):
        '''Handle a response for a list of models
        '''
        cfg = request.config
        params.update(request.url_data)
        limit = params.pop(cfg['API_LIMIT_KEY'], None)
        offset = params.pop(cfg['API_OFFSET_KEY'], None)
        with self.session(request) as session:
            query = self.query(request, session, *filters)
            return self.query_response(request, query, limit=limit,
                                       offset=offset, **params)

    def query_response(self, request, query, limit=None, offset=None,
                       text=None, sortby=None, max_limit=None, **params):
        limit = self.limit(request, limit, max_limit)
        offset = self.offset(request, offset)
        text = self.search_text(request, text)
        sortby = request.url_data.get('sortby', sortby)
        query = self.filter(request, query, text, params)
        total = query.count()
        query = self.sortby(request, query, sortby)
        data = query.limit(limit).offset(offset).all()
        data = self.serialise(request, data, **params)
        data = request.app.pagination(request, data, total, limit, offset)
        return Json(data).http_response(request)

    def filter(self, request, query, text, params):
        columns = self.columnsMapping(request.app)

        for key, value in params.items():
            bits = key.split(':')
            field = bits[0]
            if field in columns:
                col = columns[field]
                op = bits[1] if len(bits) == 2 else 'eq'
                field = col.get('field')
                if field:
                    query = self._do_filter(request, query, field, op, value)
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

    def meta(self, request, exclude=None):
        '''Return an object representing the metadata for the model
        served by this router
        '''
        columns = self.columns_with_permission(request, READ)
        #
        # Don't include columns which are excluded from meta
        exclude = set(exclude or ())
        exclude.update(self._exclude)
        if exclude:
            columns = [c for c in columns if c['name'] not in exclude]

        permissions = self.get_permissions(request)

        meta = {'id': self.id_field,
                'repr': self.repr_field,
                'columns': columns,
                'default-limit': request.config['API_LIMIT_DEFAULT']}
        if permissions:
            meta['permissions'] = permissions
        return meta

    def serialise_model(self, request, data, **kw):
        '''Serialise on model
        '''
        return self.tojson(request, data)

    def get_permissions(self, request):
        perms = {}
        self._add_permission(request, perms, 'UPDATE', self.updateform)
        self._add_permission(request, perms, 'CREATE', self.form)
        self._add_permission(request, perms, 'DELETE', True)
        return perms

    def _do_sortby(self, request, query, entry, direction):
        raise NotImplementedError

    def _do_filter(self, request, query, field, op, value):
        raise NotImplementedError

    def _add_to_app(self, app):
        model = copy(self)
        model._app = app
        return model

    def _load_columns(self, app):
        '''List of column definitions
        '''
        input_columns = self._columns or []
        columns = []

        for info in input_columns:
            col = RestColumn.make(info)
            if col.name in self._hidden:
                col.hidden = True
            columns.append(col.as_dict())

        return columns

    def _add_permission(self, request, perms, name, avail):
        if avail:
            backend = request.cache.auth_backend
            code = PERMISSION_LEVELS[name]
            if backend.has_permission(request, self.name, code):
                perms[name] = True


class ModelMixin:
    '''Mixin for accessing Rest models from the application object
    '''
    RestModel = RestModel
    _model = None

    def set_model(self, model):
        '''Set the default model for this mixin
        '''
        assert model
        if isinstance(model, str):
            model = self.RestModel(model)
        self._model = model

    def model(self, app, model=None):
        '''Return a :class:`.RestModel` model registered with ``app``.

        If ``model`` is not available, uses the :attr:`._model`
        attribute.
        '''
        app = app.app
        rest_models = getattr(app, '_rest_models', None)
        if rest_models is None:
            rest_models = {}
            app._rest_models = rest_models

        if not model:
            if hasattr(self._model, '__call__'):
                self._model = self._model()
            model = self._model

        assert model, 'No model specified'

        if isinstance(model, RestModel):
            url = model.url
            if url not in rest_models:
                rest_models[url] = model._add_to_app(app)
        else:
            url = model

        if url in rest_models:
            return rest_models[url]
        else:
            raise RuntimeError('model url "%s" not available' % url)

    def check_model_permission(self, request, level, model=None):
        """
        Checks whether the user has the requested level of access to
        the model, raising PermissionDenied if not

        :param request:     request object
        :param level:       access level
        :raise:             PermissionDenied
        """
        model = self.model(request, model)
        backend = request.cache.auth_backend
        if not backend.has_permission(request, model.name, level):
            raise PermissionDenied
