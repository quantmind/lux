from datetime import date, datetime

from sqlalchemy_utils.functions import get_columns

from lux.extensions import rest


class RestModel(rest.RestModel):
    '''A rest model based on SqlAlchemy ORM
    '''

    def _load_columns(self, app):
        '''List of column definitions
        '''
        columns = self._columns or []
        model = app.odm()[self.name]
        cols = get_columns(model)._data
        for attrname, col in cols.items():
            info = {'attrname': attrname,
                    'name': col.name,
                    'type': python_type(col.type)}
            columns.append(info)
        return columns


def python_type(t):
    return _types.get(t.python_type, 'string')


_types = {int: 'integer',
          bool: 'boolean',
          date: 'date',
          datetime: 'datetime'}
