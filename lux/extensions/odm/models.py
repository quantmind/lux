import json
from datetime import date, datetime

import pytz

from sqlalchemy import Column

from pulsar.utils.html import nicename

from odm.utils import get_columns

from lux.extensions import rest


RestColumn = rest.RestColumn


class RestModel(rest.RestModel):
    '''A rest model based on SqlAlchemy ORM
    '''
    def session(self, request):
        return request.app.odm().begin()

    def tojson(self, request, obj, exclude=None):
        '''Override the method from the base class.

        It uses sqlalchemy model information about columns
        '''
        exclude = set(exclude or ())
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

        for info in input_columns:
            col = RestColumn.make(info)
            dbcol = cols.pop(col.name, None)
            # If a database column
            if isinstance(dbcol, Column):
                info = column_info(col.name, dbcol)
                info.update(col.as_dict())
            else:
                info = col.as_dict(True)

            columns.append(info)

        for name, col in cols.items():
            if name not in self._exclude:
                columns.append(column_info(name, col))

        return columns


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
