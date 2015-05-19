from sqlalchemy_utils.functions import get_columns

from lux.extensions import rest


class RestModel(rest.RestModel):
    '''A rest model based on SqlAlchemy ORM
    '''
    _columns = None
    _loaded = False

    def __init__(self, model, addform=None, editform=None,
                 columns=None):
        super().__init__(addform, editform)
        self.model = model
        self._columns = columns

    def columns(self, app):
        if not self._loaded:
            columns = self._columns or []
            model = app.odm()[self.model]
            self._columns = odm_columns(model, columns)
            self._loaded = True
        return self._columns


def odm_columns(model, columns):
    cols = get_columns(model)
    for col in columns:
        pass
