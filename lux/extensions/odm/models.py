import json
from datetime import date, datetime
from enum import Enum

import pytz

from sqlalchemy import Column

from pulsar.utils.html import nicename

from odm.utils import get_columns

from lux.extensions import rest


class RelatedMixin:

    def __init__(self, model):
        assert model, 'no model defined'
        self._model = model

    @property
    def model(self):
        '''Allow model to be defined as a function for circular references
        reasons
        '''
        if not isinstance(self._model, RestModel):
            if hasattr(self._model, '__call__'):
                self._model = self._model()
            else:
                self._model = RestModel(self._model)
        return self._model


class RestColumn(rest.RestColumn):
    pass


class ModelColumn(RestColumn, RelatedMixin):

    def __init__(self, name, model=None, **kwargs):
        super().__init__(name, **kwargs)
        RelatedMixin.__init__(self, model)


class RestModel(rest.RestModel):
    '''A rest model based on SqlAlchemy ORM
    '''
    _db_columns = None
    _rest_columns = None

    def session(self, request):
        '''Obtain a session
        '''
        return request.app.odm().begin()

    def db_model(self):
        '''Database model
        '''
        assert self._app, 'ODM Rest Model not loaded'
        return self._app.odm()[self.name]

    def db_columns(self, columns):
        '''Return a list of columns available in the database table
        '''
        assert self._db_columns, 'ODM Rest Model not loaded'
        return [c for c in columns if c in self._db_columns]

    def tojson(self, request, obj, exclude=None):
        '''Override the method from the base class.

        It uses sqlalchemy model information about columns
        '''
        exclude = set(exclude or ())
        exclude.update(self._exclude)
        columns = self.columns(request.app)

        fields = {}
        for col in columns:
            name = col['name']
            restcol = self._rest_columns[name]
            if name in exclude:
                continue
            try:
                data = obj.__getattribute__(name)
                if hasattr(data, '__call__'):
                    data = data()
                if isinstance(data, date):
                    if isinstance(data, datetime) and not data.tzinfo:
                        data = pytz.utc.localize(data)
                    data = data.isoformat()
                elif isinstance(data, Enum):
                    data = data.name
                elif isinstance(restcol, ModelColumn):
                    data = self._related_model(request, restcol.model, data)
                else:   # Test Json
                    json.dumps(data)
            except TypeError:
                continue
            if data is not None:
                fields[name] = data
        # a json-encodable dict
        return fields

    def id_repr(self, request, obj):
        data = {'id': getattr(obj, self.id_field)}
        if self.repr_field != self.id_field:
            data['repr'] = getattr(obj, self.repr_field)
        return data

    def _load_columns(self):
        '''List of column definitions
        '''
        model = self.db_model()
        self._db_columns = get_columns(model)
        self._rest_columns = {}
        input_columns = self._columns or []
        cols = self._db_columns._data.copy()
        columns = []

        for info in input_columns:
            col = RestColumn.make(info)
            if col.name not in self._rest_columns:
                dbcol = cols.pop(col.name, None)
                # If a database column
                if isinstance(dbcol, Column):
                    info = column_info(col.name, dbcol)
                    info.update(col.as_dict(defaults=False))
                else:
                    info = col.as_dict()
                self._append_col(col, columns, info)

        for name, col in cols.items():
            if name not in self._rest_columns:
                self._append_col(col, columns, column_info(name, col))

        return columns

    def _append_col(self, col, columns, info):
        name = info['name']
        self._rest_columns[name] = col
        if name in self._hidden:
            info['hidden'] = True
        columns.append(info)

    def _related_model(self, request, model, obj):
        if isinstance(obj, list):
            return [self._related_model(request, model, d) for d in obj]
        else:
            return model.id_repr(request, obj)


def column_info(name, col):
    sortable = True
    filter = True
    try:
        type = _types.get(col.type.python_type, 'string')
    except NotImplementedError:
        type = col.type.__class__.__name__.lower()
        sortable = False
        filter = False

    info = {'name': name,
            'field': col.name,
            'displayName': col.doc or nicename(name),
            'sortable': sortable,
            'filter': filter,
            'type': type}

    return info


_types = {int: 'integer',
          bool: 'boolean',
          date: 'date',
          datetime: 'datetime'}
