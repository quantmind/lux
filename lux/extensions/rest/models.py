import json
import logging
from inspect import isgenerator
from urllib.parse import urljoin

from pulsar import PermissionDenied
from pulsar.utils.html import nicename
from pulsar.apps.wsgi import Json
from pulsar.utils.httpurl import is_absolute_uri
from pulsar.utils.log import lazymethod

from lux.core import LuxModel


logger = logging.getLogger('lux.extensions.rest')


class RestColumn:
    """A class for specifying attributes of a REST column/field
    for a model
    """

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
    """Mixin for managing model permissions at column (field) level

    This mixin can be used by any class.
    """
    def column_fields(self, columns, field=None):
        """Return a list column fields from the list of columns object
        """
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
            columns = self.columns()
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
        columns = self.columns()
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
        columns = self.columns()
        perms = self.column_permissions(request, level)
        return tuple((col for col in columns if not perms.get(col['name'])))


class RestClient:
    """Implemets method accessed by clients to Rest Models
    """
    def get_target(self, request, **extra_data):
        """Get a target object for this model

        Used by HTML Router to get information about the LUX REST API
        of this Rest Model
        """
        app = request.app
        api_url = self.api_url or app.config.get('API_URL')
        if not api_url:
            return
        target = {'url': api_url, 'name': self.api_name}
        target.update(**extra_data)
        return target

    def field_options(self, request, **extra_data):
        """Return a generator of options for a html serializer
        """
        if not request:
            logger.error('%s cannot get remote target. No request', self)
            return
        target = self.get_target(request, **extra_data)
        yield 'data-remote-options', json.dumps(target)
        yield 'data-remote-options-id', self.id_field
        yield 'data-remote-options-value', json.dumps({
            'type': 'field',
            'source': self.repr_field})
        yield 'data-ng-options', self.remote_options_str.format(
            options=self.api_name)
        yield 'data-ng-options-ui-select', \
            self.remote_options_str_ui_select.format(options=self.api_name)


class RestModel(LuxModel, RestClient, ColumnPermissionsMixin):
    """Hold information about a model used for REST views

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
    """
    remote_options_str = 'item.id as item.name for item in {options}'
    remote_options_str_ui_select = 'item.id as item in {options}'

    def __init__(self, name, form=None, updateform=None, columns=None,
                 url=None, api_name=None, exclude=None,
                 api_url=None, html_url=None, id_field=None,
                 repr_field=None, hidden=None):
        assert name, 'model name not available'
        self.name = name
        self.form = form
        self.updateform = updateform
        self.url = url if url is not None else '%ss' % name
        self.api_name = '%s_url' % self.url.replace('/', '_')
        self.id_field = id_field or 'id'
        self.repr_field = repr_field or 'id'
        self.html_url = html_url
        self.api_url = api_url
        self._columns = columns
        self._exclude = set(exclude or ())
        self._hidden = set(hidden or ())

    def __repr__(self):
        return self.name
    __str__ = __repr__

    @property
    def identifier(self):
        return self.url

    @lazymethod
    def columnsMapping(self):
        """Returns a dictionary of names/columns objects
        """
        return dict(((c['name'], c) for c in self.columns()))

    def limit(self, request, limit=None, max_limit=None):
        """The maximum number of items to return when fetching list of data
        """
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
        """Retrieve the offset value from the url when fetching list of data
        """
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
        if isinstance(data, list) or isgenerator(data):
            kw['in_list'] = True
            return [self.serialise_model(request, o, **kw) for o in data]
        else:
            return self.serialise_model(request, data)

    def collection_data(self, request, *filters, **params):
        """Handle a response for a list of models
        """
        cfg = request.config
        params.update(request.url_data)
        limit = params.pop(cfg['API_LIMIT_KEY'], None)
        offset = params.pop(cfg['API_OFFSET_KEY'], None)
        with self.session(request) as session:
            query = self.query(request, session, *filters)
            return self.query_data(request, query, limit=limit,
                                   offset=offset, **params)

    def query_data(self, request, query, limit=None, offset=None,
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
        return request.app.pagination(request, data, total, limit, offset)

    def collection_response(self, request, *filters, **params):
        data = self.collection_data(request, *filters, **params)
        return Json(data).http_response(request)

    def query_response(self, request, query, **kwargs):
        data = self.query_data(request, query, **kwargs)
        return Json(data).http_response(request)

    def filter(self, request, query, text, params):
        columns = self.columnsMapping()

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
        """Return an object representing the metadata for the model
        served by this router
        """
        columns = self.columns_with_permission(request, 'read')
        #
        # Don't include columns which are excluded from meta
        exclude = set(exclude or ())
        exclude.update(self._exclude)
        if exclude:
            columns = [c for c in columns if c['name'] not in exclude]

        backend = request.cache.auth_backend
        permissions = backend.get_permissions(request, self.name)
        permissions = permissions.get(self.name, {})
        if not self.updateform:
            permissions['update'] = False
        if not self.form:
            permissions['create'] = False

        meta = {'id': self.id_field,
                'repr': self.repr_field,
                'columns': columns,
                'default-limit': request.config['API_LIMIT_DEFAULT']}
        if permissions:
            meta['permissions'] = permissions
        return meta

    def get_instance(self, request, **args):
        raise NotImplementedError

    def serialise_model(self, request, data, **kw):
        """Serialise on model
        """
        return self.tojson(request, data)

    def get_url(self, request, path):
        return self._build_url(request, path, self.url,
                               request.config.get('API_URL'))

    def get_html_url(self, request, path):
        return self._build_url(request,
                               path,
                               self.html_url,
                               request.config.get('WEB_SITE_URL'))

    def _do_sortby(self, request, query, entry, direction):
        raise NotImplementedError

    def _do_filter(self, request, query, field, op, value):
        raise NotImplementedError

    def _load_columns(self):
        """List of column definitions
        """
        input_columns = self._columns or []
        columns = []

        for info in input_columns:
            col = RestColumn.make(info)
            if col.name in self._hidden:
                col.hidden = True
            columns.append(col.as_dict())

        return columns

    def _build_url(self, request, path, url, base):
        if url is None:
            return
        if not is_absolute_uri(url):
            base = base or request.absolute_uri('/')
            url = urljoin(base, url)
            if not is_absolute_uri(url):
                base = request.absolute_uri('/')
                url = urljoin(base, url)
        if path:
            if path.startswith('/'):
                path = path[1:]
            if path:
                if not url.endswith('/'):
                    url = '%s/' % url
                url = '%s%s' % (url, path)
        return url


class ModelMixin:
    """Mixin for accessing Rest models from the application object
    """
    RestModel = RestModel
    model = None

    def set_model(self, model):
        """Set the default model for this mixin
        """
        assert model
        if isinstance(model, str):
            model = self.RestModel(model)
        self.model = model

    def check_model_permission(self, request, level, model=None):
        """
        Checks whether the user has the requested level of access to
        the model, raising PermissionDenied if not

        :param request:     request object
        :param level:       access level
        :raise:             PermissionDenied
        """
        model = self.model
        backend = request.cache.auth_backend
        if not backend.has_permission(request, model.name, level):
            raise PermissionDenied
