from datetime import date, datetime

from sqlalchemy_utils.functions import get_columns

from pulsar.utils.html import nicename

from lux.extensions import rest


class RestModel(rest.RestModel):
    '''A rest model based on SqlAlchemy ORM
    '''

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
    type, sortable = python_type(col.type)
    info = {'name': name,
            'field': col.name,
            'displayName': nicename(name),
            'sortable': sortable,
            'type': type}
    return info


def python_type(t):
    try:
        return _types.get(t.python_type, 'string'), True
    except NotImplementedError:
        return t.__class__.__name__.lower(), False


_types = {int: 'integer',
          bool: 'boolean',
          date: 'date',
          datetime: 'datetime'}
