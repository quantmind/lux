from sqlalchemy import Table
from sqlalchemy.ext.declarative import DeclarativeMeta

import odm


model_base = odm.model_base
cache_name = '__odm_models__'


def is_model(cls):
    return isinstance(cls, (Table, DeclarativeMeta))


class Mapper(odm.Mapper):
    '''SQLAlchemy wrapper for lux applications
    '''

    def __init__(self, app, binds):
        self.app = app
        super().__init__(binds)
        for model in self.app.module_iterator('models', is_model, cache_name):
            self.register(model)

    def copy(self, binds):
        return self.__class__(self.app, binds)

    def session(self, **options):
        options['binds'] = self.binds
        return LuxSession(self, **options)


class LuxSession(odm.OdmSession):

    @property
    def app(self):
        return self.mapper.app
