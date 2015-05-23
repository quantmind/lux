import json
from datetime import date, datetime

import pytz

from sqlalchemy_utils.functions import get_columns

from pulsar.utils.html import nicename

from lux.extensions import rest


class RestModel(rest.RestModel):
    '''A rest model based on SqlAlchemy ORM
    '''
    def tojson(self, obj, exclude=None):
        exclude = set(exclude or ())
        columns = get_columns(obj)

        fields = {}
        for field in columns:
            try:
                data = obj.__getattribute__(field.name)
                if isinstance(data, date):
                    if isinstance(data, datetime) and not data.tzinfo:
                        data = pytz.utc.localize(data)
                    data = data.isoformat()
                else:   # Test Json
                    json.dumps(data)
            except TypeError:
                continue
            if data is not None:
                fields[field.name] = data
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
            name = info['name']
            col = cols.pop(name, None)
            if col:
                default = column_info(name, col)
                default.update(info)
                info = default
            columns.append(info)

        for name, col in cols.items():
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
            'displayName': nicename(name),
            'sortable': sortable,
            'filter': filter,
            'type': type}
    return info


_types = {int: 'integer',
          bool: 'boolean',
          date: 'date',
          datetime: 'datetime'}
