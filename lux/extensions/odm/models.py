from datetime import date, datetime

from sqlalchemy_utils.functions import get_columns

from lux.extensions import rest


class RestModel(rest.RestModel):
    '''A rest model based on SqlAlchemy ORM
    '''
    _columns = None
    _loaded = False

    def __init__(self, model, addform=None, editform=None, columns=None):
        super().__init__(addform, editform)
        self.name = model
        self._columns = columns

    def columns(self, app):
        '''List of column definitions
        '''
        if not self._loaded:
            columns = self._columns or []
            model = app.odm()[self.name]
            self._columns = odm_columns(model, columns)
            self._loaded = True
        return self._columns


def odm_columns(model, columns):
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
