import logging
from inspect import isgenerator
from urllib.parse import urljoin, urlparse, urlunparse

from pulsar import PermissionDenied
from pulsar.utils.html import nicename
from pulsar.apps.wsgi import Json
from pulsar.utils.httpurl import is_absolute_uri, remove_double_slash
from pulsar.utils.log import lazymethod

from lux.core import LuxModel

from .client import url_path


logger = logging.getLogger('lux.extensions.rest')


class RestColumn:
    """A class for specifying attributes of a REST column/field
    for a model

    .. attribute:: sotable

        Can be sorted or not

    .. attribute:: hidden

        Can be hidden when displayed by a rest client (in a table for example)

    .. attribute:: model

        If available, this column is related to another model
    """

    def __init__(self, name, sortable=None, filter=None, type=None,
                 displayName=None, field=None, hidden=None, model=None):
        self.name = name
        self.sortable = sortable
        self.filter = filter
        self.type = type
        self.displayName = displayName
        self.field = field
        self.hidden = hidden
        self.model = model

    @classmethod
    def make(cls, col):
        if isinstance(col, RestColumn):
            return col
        assert isinstance(col, str), 'Not a string'
        return cls(col)

    def __repr__(self):  # pragma    nocover
        return self.name

    __str__ = __repr__

    def as_dict(self, model, defaults=True):
        if self.model:
            if self.field:
                model._exclude.add(self.field)
            if not self.type:
                self.type = 'object'
        return dict(self._as_dict(defaults))

    def set(self, instance, value):
        setattr(instance, self.name, value)

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


def is_rel_column(col):
    """Check if an object is a Rest Column for a related model
    """
    return isinstance(col, RestColumn) and col.model


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
    def get_target(self, request, **params):
        """Get a target object for this model

        Used by HTML Router to get information about the LUX REST API
        of this Rest Model
        """
        app = request.app
        api_url = self.api_url or app.config.get('API_URL')
        if not api_url:
            return
        url = list(urlparse(api_url))
        url[2] = remove_double_slash('%s/%s' % (url[2], self.url))
        url = urlunparse(url)

        target = {
            'id_field': self.id_field,
            'repr_field': self.repr_field,
            'url': url
        }
        #
        # Add additional parameters
        for key, value in params.items():
            if hasattr(value, '__call__'):
                value = value(request)
            if value is not None:
                target[key] = value

        return target


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

    def serialise(self, request, data, **kw):
        if isinstance(data, list) or isgenerator(data):
            kw['in_list'] = True
            return [self.serialise_model(request, o, **kw) for o in data]
        else:
            return self.serialise_model(request, data)

    def serialise_model(self, request, obj, exclude=None, **kw):
        """
        Makes a model instance JSON-friendly. Removes fields that the
        user does not have read access to.

        :param request:     request object
        :param data:        data
        :return:            dict
        """
        exclude = set(exclude or ())
        fields = self.columns_without_permission(request, 'read')
        exclude.update(self.column_fields(fields, 'name'))
        model = self.tojson(request, obj, exclude=exclude, **kw)
        if self.id_field not in model and self.id_field not in exclude:
            model[self.id_field] = getattr(obj, self.id_field)
        if 'url' not in exclude:
            model['url'] = self.get_url(request, model[self.id_field])
        return model

    def collection_data(self, request, *filters, **params):
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
        with self.session(request) as session:
            query = self.query(request, session, *filters)
            return self.query_data(request, query, **params)

    def query_data(self, request, query, limit=None, offset=None,
                   search=None, sortby=None, max_limit=None, **params):
        """Application query method

        This method does not use url data
        """
        limit = self.limit(request, limit, max_limit)
        offset = get_offset(offset)
        query = self.filter(request, query, search, params)
        total = query.count()
        query = self.sortby(request, query, sortby)
        data = query.limit(limit).offset(offset).all()
        data = self.serialise(request, data, **params)
        return request.app.pagination(request, data, total, limit, offset)

    def collection_response(self, request, *filters, **params):
        data = self.collection_data(request, *filters, **params)
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

    def add_related_column(self, name, model, field=None, **kw):
        '''Add a related column to the model
        '''
        assert not self._app, 'already loaded'
        if field:
            self._exclude.add(field)
        column = RestColumn(name, field=field, model=model, **kw)
        cols = list(self._columns or ())
        cols.append(column)
        self._columns = cols

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
            columns.append(col.as_dict(self))

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
        return url_path(url, path)


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


def get_offset(offset=None):
    try:
        offset = int(offset)
    except Exception:
        offset = 0
    return max(0, offset)
