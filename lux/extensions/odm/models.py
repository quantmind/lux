import json
from datetime import date, datetime
from enum import Enum

import pytz

from sqlalchemy import Column

from pulsar.utils.html import nicename

from odm.utils import get_columns

from lux.extensions import rest


class RestColumn(rest.RestColumn):
    pass


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


class RestModel(rest.RestModel):
    '''A rest model based on SqlAlchemy ORM
    '''
    def session(self, request):
        '''Obtain a session
        '''
        return request.app.odm().begin()

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
                else:   # Test Json
                    json.dumps(data)
            except TypeError:
                continue
            if data is not None:
                fields[name] = data
        # a json-encodable dict
        return fields

    def _load_columns(self, app):
        '''List of column definitions
        '''
        input_columns = self._columns or []
        model = app.odm()[self.name]
        cols = get_columns(model)._data.copy()
        columns = []
        all = set()

        for info in input_columns:
            col = RestColumn.make(info)
            if col.name not in all:
                dbcol = cols.pop(col.name, None)
                # If a database column
                if isinstance(dbcol, Column):
                    info = column_info(col.name, dbcol)
                    info.update(col.as_dict(defaults=False))
                else:
                    info = col.as_dict()
                self._append_col(all, columns, info)

        for name, col in cols.items():
            if name not in all:
                self._append_col(all, columns, column_info(name, col))

        return columns

    def _append_col(self, all, columns, info):
        name = info['name']
        all.add(name)
        if name in self._hidden:
            info['hidden'] = True
        columns.append(info)


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
