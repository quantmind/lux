from itertools import chain
from collections import Mapping, OrderedDict
from urllib.parse import urljoin

from pulsar.utils.html import nicename
from pulsar.utils.httpurl import is_absolute_uri

from lux.core import LuxModel

from .client import url_path


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
        self.type = type
        self.displayName = displayName
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

    def tojson(self, model=None, defaults=True):
        if self.model:
            if self.field:
                model._fields.add_exclude(self.field)
            if not self.type:
                self.type = 'object'
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


URL_FIELDS = (
    RestField('api_url', displayName='Url', type='url', hidden=True).tojson(),
    RestField('html_url', type='url', hidden=True).tojson()
)


def is_rel_field(col):
    """Check if an object is a Rest Column for a related model
    """
    return isinstance(col, RestField) and col.model


class RestClient:
    """Implements the method accessed by clients of lux Rest API
    """
    def api_url(self, request, id=None):
        base = request.config.get('API_URL')
        if base:
            if not is_absolute_uri(base):
                base = request.absolute_uri('/')
            if base.endswith('/'):
                base = base[:-1]
            base = '%s/%s' % (base, self._url)
            return '%s/%s' % (base, id) if id else base

    def get_target(self, request, **params):
        """Get a target object for this model

        Used by HTML Router to get information about the LUX REST API
        of this Rest Model
        """
        api_url = self.api_url(request)
        if not api_url:
            return
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

    def __init__(self, urls, include, exclude, hidden):
        self.urls = urls
        self.include = include
        self.hidden = hidden
        self._exclude = exclude

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

    def __init__(self, name, form=None, updateform=None, fields=None,
                 url=None, exclude=None, html_url=None, id_field=None,
                 repr_field=None, hidden=None):
        assert name, 'model name not available'
        self.name = name
        self.form = form
        self.updateform = updateform
        self._url = url if url is not None else '%ss' % name
        self._html_url = html_url
        self.api_name = '%s_url' % self._url.replace('/', '_')
        self.id_field = id_field or 'id'
        self.repr_field = repr_field or self.id_field
        self._fields = self._fields(
            urls=tuple((f['name'] for f in URL_FIELDS)),
            include=list(chain(fields or (), URL_FIELDS)),
            exclude=set(exclude or ()),
            hidden=set(hidden or ())
        )

    def __repr__(self):
        return self.name
    __str__ = __repr__

    @property
    def identifier(self):
        return self._url

    def fields(self):
        return self._fields.load(self).map

    def column_fields(self, fields, field=None):
        """Return a list column fields from the list of fields object
        """
        field = field or 'field'
        fields = set()
        for c in fields:
            value = c[field]
            if isinstance(value, (tuple, list)):
                fields.update(value)
            else:
                fields.add(value)
        return tuple(fields)

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
        """
        Makes a model instance JSON-friendly. Removes fields that the
        user does not have read access to.

        :param request:     WSGI request
        :param obj:         model instance
        :param load_only:   Optional list of fields to load
        :return:            dict
        """
        if self.id_field not in data:
            id_value = instance.id
        else:
            id_value = data[self.id_field]
        for url_name in self._fields.urls:
            method = getattr(self, url_name, None)
            if method and (not instance.fields or url_name in instance.fields):
                data[url_name] = method(request, id_value)
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
             check_permission=None):
        """Return an object representing the metadata for the model
        served by this router
        """
        fields = self.fields()
        field_names = self.fields_with_permission(request, 'read')
        #
        # Don't include fields which are excluded from meta
        exclude = self._fields.exclude(exclude)
        if exclude:
            field_names = [c for c in field_names if c not in exclude]

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
                'columns': [fields[name].tojson(self) for name in field_names],
                'default-limit': request.config['API_LIMIT_DEFAULT']}
        if permissions:
            meta['permissions'] = permissions

        with self.session(session) as session:
            query = self.query(request, session).filter(*filters)
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

    def html_url(self, request, path):
        return self._build_url(request,
                               path,
                               self._html_url,
                               request.config.get('WEB_SITE_URL'))

    def _load_fields_map(self, rest):
        """List of column definitions
        """
        fields = self._fields

        for info in fields.include:
            col = RestField.make(info)
            if col.name in fields.hidden:
                col.hidden = True
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


class ModelMixin:
    """Mixin for accessing Rest models from the application object
    """


def get_offset(offset=None):
    try:
        offset = int(offset)
    except Exception:
        offset = 0
    return max(0, offset)
