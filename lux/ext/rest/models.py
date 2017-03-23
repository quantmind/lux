from copy import copy
from itertools import chain
from collections import Mapping, OrderedDict
from urllib.parse import urljoin, urlparse, urlunparse

from pulsar.utils.html import nicename
from pulsar.utils.httpurl import is_absolute_uri


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

