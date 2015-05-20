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
    info = {'name': name,
            'field': col.name,
            'displayName': nicename(name),
            'sortable': True,
            'type': python_type(col.type)}
    return info


def python_type(t):
    return _types.get(t.python_type, 'string')


_types = {int: 'integer',
          bool: 'boolean',
          date: 'date',
          datetime: 'datetime'}
