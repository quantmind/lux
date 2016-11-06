from copy import copy
from itertools import chain
from collections import Mapping, OrderedDict
from urllib.parse import urljoin, urlparse, urlunparse

from pulsar.utils.html import nicename
from pulsar.utils.httpurl import is_absolute_uri

from lux.core import LuxModel, GET_HEAD

from .query import Query, RestSession


CONVERTERS = {
    'int': lambda value: int(value),
    'float': lambda value: float(value)
}


class RestField:
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
        self.type = type or ('object' if model else 'string')
        self.displayName = displayName or nicename(name)
        self.field = field
        self.hidden = hidden
        self.model = model

    @classmethod
    def make(cls, col):
        if isinstance(col, RestField):
            return col
        if isinstance(col, str):
            return cls(col)
        elif isinstance(col, Mapping):
            col = col.copy()
            name = col.pop('name', None)
            if not name:
                raise ValueError('name not provided')
            return cls(name, **col)
        else:
            raise ValueError('Expected string or Mapping got %s' % type(col))

    def __repr__(self):  # pragma    nocover
        return self.name

    __str__ = __repr__

    def tojson(self):
        return dict(self._as_dict())

    def value(self, value):
        converter = CONVERTERS.get(self.type)
        try:
            return converter(value)
        except Exception:
            return value

    def _as_dict(self):
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue
            if v is not None:
                yield k, v


URL_FIELDS = (
    RestField('api_url', type='url', hidden=True).tojson(),
    RestField('html_url', type='url', hidden=True).tojson()
)


def is_rel_field(col):
    """Check if an object is a Rest Column for a related model
    """
    return isinstance(col, RestField) and col.model


class RestClient:
    """Implements the method accessed by clients of lux Rest API
    """
    def model_url_params(self, request, idvalue=None, **kwargs):
        params = {}
        if idvalue is not None:
            params[self.id_field] = idvalue
        for name in self.api_route.variables:
            if name not in kwargs:
                value = request.urlargs.get(name)
            else:
                value = kwargs[name]
            params[name] = value
        return params

    def api_url(self, request, instance=None, **kwargs):
        apis = request.app.apis
        if apis and self.api_route:
            api = apis.get(self.api_route)
            if api is None:
                return
            params = {}
            for name in self.api_route.variables:
                if name not in kwargs:
                    if instance:
                        value = self.get_instance_value(instance, name)
                    else:
                        value = request.urlargs.get(name)
                    if not value:
                        request.logger.error('Could not evaluate url for %s',
                                             self)
                        return
                else:
                    value = kwargs[name]
                params[name] = value
            path = self.api_route.url(**params)
            if instance:
                path = '%s/%s' % (path, instance.id)
            return api.url(request, path)

    def get_target(self, request, **params):
        """Get a target object for this model

        Used by HTML Router to get information about the LUX REST API
        of this Rest Model
        """
        api_url = self.api_url(request, **params)
        if not api_url:
            return
        for name in self.api_route.variables:
            params.pop(name, None)

        target = {
            'id_field': self.id_field,
            'repr_field': self.repr_field,
            'url': api_url
        }
        #
        # Add additional parameters
        for key, value in params.items():
            if hasattr(value, '__call__'):
                value = value(request)
            if value is not None:
                target[key] = value

        return target


class FieldsInfo:
    map = None

    def __init__(self, urls, include, exclude, hidden, list_exclude):
        self.urls = urls
        self.include = include
        self.hidden = hidden
        self._exclude = exclude
        self._list_exclude = list_exclude

    def exclude(self, exclude=None, exclude_urls=False):
        exclude = set(exclude or ())
        exclude.update(self._exclude)
        if exclude_urls:
            exclude.update(self.urls)
        return exclude

    def add_exclude(self, exclude):
        self._exclude.add(exclude)

    def add_include(self, include):
        assert self.map is None
        self.include.append(include)

    def load(self, model):
        if self.map is None:
            self.map = model._load_fields_map(OrderedDict())
        return self


class RestModel(LuxModel, RestClient):
    """Hold information about a model used for REST views

    .. attribute:: name

        name of this REST model

    .. attribute:: identifier

        unique string identifier of this REST model (by default the plural
        of :attr:`.name`)

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
        set to True in the :class:`.RestField` metadata
    """
    _fields = FieldsInfo
    api_route = None
    spec = None
    json_docs = None

    def __init__(self, name, form=None, updateform=None,
                 putform=None, postform=None, fields=None,
                 url=None, exclude=None, html_url=None, id_field=None,
                 repr_field=None, hidden=None, list_exclude=None,
                 spec=None, json_docs=None):
        assert name, 'model name not available'
        self.name = name
        self.form = form
        self.updateform = updateform
        self.postform = postform
        self.putform = putform
        self.spec = spec or self.spec
        self.json_docs = json_docs or self.json_docs or {}
        self._url = url if url is not None else '%ss' % name
        self._html_url = html_url
        self.api_name = '%s_url' % self._url.replace('/', '_')
        self.id_field = id_field or 'id'
        self.repr_field = repr_field or self.id_field
        self._fields = self._fields(
            urls=tuple((f['name'] for f in URL_FIELDS)),
            include=list(chain(fields or (), URL_FIELDS)),
            exclude=set(exclude or ()),
            hidden=set(hidden or ()),
            list_exclude=set(list_exclude or ())
        )

    def __repr__(self):
        return self.name
    __str__ = __repr__

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        cls = self.__class__
        model = cls.__new__(cls)
        model.__dict__ = self.__dict__.copy()
        model.api_route = None
        model._fields = copy(self._fields)
        return model

    @property
    def identifier(self):
        return self._url

    def fields(self):
        return self._fields.load(self).map

    def instance_verbs(self):
        methods = set(GET_HEAD)
        methods.add('DELETE')
        if self.updateform:
            methods.add('PATCH')
        if self.postform:
            methods.add('POST')
        if self.putform:
            methods.add('PUT')
        return methods

    def column_fields(self, fields):
        """Return a list column fields from the list of fields object
        """
        field_names = set()
        for name in fields:
            field = self.field(name)
            if field:
                if isinstance(field.field, (tuple, list)):
                    field_names.update(field.field)
                elif field.field:
                    field_names.add(field.field)
        return tuple(field_names)

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

    def instance_urls(self, request, instance, data):
        for url_name in self._fields.urls:
            method = getattr(self, url_name, None)
            if method and (not instance.fields or url_name in instance.fields):
                url = method(request, instance)
                if url:
                    data[url_name] = url
        return data

    def query_data(self, request, *filters, limit=None, offset=None,
                   sortby=None, max_limit=None, session=None, **params):
        """Application query method

        This method does not use url data
        """
        with self.session(request, session=session) as session:
            query = self.query(request, session, *filters, **params)
            limit = self.limit(request, limit, max_limit)
            offset = get_offset(offset)
            total = query.count()
            query = query.sortby(sortby).limit(limit).offset(offset)
            data = query.tojson(request, **params)
            return request.app.pagination(request, data, total, limit, offset)

    def meta(self, request, *filters, exclude=None, session=None,
             check_permission=None, **params):
        """Return an object representing the metadata for the model
        served by this router
        """
        fields = self.fields()

        if check_permission:
            fnames = check_permission(request)
        else:
            fnames = tuple(fields)
        #
        # Don't include fields which are excluded from meta
        exclude = self._fields.exclude(exclude)
        if exclude:
            fnames = [c for c in fnames if c not in exclude]

        backend = request.cache.auth_backend
        permissions = backend.get_permissions(request, self.name)
        permissions = permissions.get(self.name, {})
        if not self.updateform:
            permissions['update'] = False
        if not self.form:
            permissions['create'] = False

        meta = {'name': self.name,
                'url': self.api_url(request),
                'id': self.id_field,
                'repr': self.repr_field,
                'columns': [fields[name].tojson() for name in fnames],
                'default-limit': request.config['API_LIMIT_DEFAULT']}
        if permissions:
            meta['permissions'] = permissions

        with self.session(request, session=session) as session:
            query = self.query(request, session, *filters, **params)
            meta['total'] = query.count()
        return meta

    def add_related_field(self, name, model, field=None, **kw):
        '''Add a related column to the model
        '''
        assert not self._app, 'already loaded'
        fields = self._fields
        if field:
            fields.add_exclude(field)
        field = RestField(name, field=field, model=model, **kw)
        fields.add_include(field)

    def html_url(self, request, instance):
        return self._build_url(request,
                               instance,
                               self._html_url,
                               request.config.get('WEB_SITE_URL'))

    def _load_fields_map(self, rest):
        """List of column definitions
        """
        fields = self._fields

        for info in fields.include:
            col = RestField.make(info)
            if col.name in rest:
                continue
            if col.name in fields.hidden:
                col.hidden = True
            if not col.field:
                col.field = col.name
            rest[col.name] = col

        return rest

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


class DictModel(RestModel):
    """A rest model with instances given by python dictionaries
    """
    def session(self, request, session=None):
        return session or RestSession(self, request)

    def get_query(self, session):
        return Query(self, session.request)

    def create_instance(self):
        return {}

    def tojson(self, request, instance, **kw):
        return self.instance(instance).obj

    def set_instance_value(self, instance, name, value):
        field = self.field(name)
        if not field:
            return
        if field.model:
            model = self.app.models.get(field.model)
            if model:
                value = model.instance(value).id
            else:
                self.app.logger.error('Related model "%s" not found in %s',
                                      field.model, self)
                return
        value = self.clean_up_value(value)
        if value is None:
            instance.obj.pop(name, None)
        else:
            instance.obj[name] = value

    def get_instance_value(self, instance, name):
        value = instance.obj.get(name)
        field = self.field(name)
        return field.value(value) if field else value

    def clean_up_value(self, value):
        if value is None:
            return value
        if isinstance(value, list):
            values = []
            for v in value:
                v = self.clean_up_value(v)
                if v:
                    values.append(v)
            return values or None
        elif isinstance(value, dict):
            for k, v in tuple(value.items()):
                v = self.clean_up_value(v)
                if not v:
                    value.pop(k)
                else:
                    value[k] = v
            return value or None
        else:
            return value


def get_offset(offset=None):
    try:
        offset = int(offset)
    except Exception:
        offset = 0
    return max(0, offset)


def url_path(base, path):
    if path:
        url = list(urlparse(base))
        path = str(path)
        if path.startswith('/'):
            url[2] = path
        elif path:
            p = url[2]
            if not p.endswith('/'):
                p = '%s/' % p
            url[2] = '%s%s' % (p, path)
        return urlunparse(url)
    return base
