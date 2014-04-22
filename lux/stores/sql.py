from collections import OrderedDict

from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta

from pulsar.apps.data import Store, register_store
from pulsar.apps.greenio import green_task



class SqlStore(Store):
    '''A pulsar :class:`.Store` based on sqlalchemy
    '''
    def _init(self, **kwargs):
        dns = self._buildurl()
        self.sql_engine = create_engine(dns, **kwargs)

    @green_task
    def connect(self):
        return self.sql_engine.connect()

    def create_table(self, model, remove_existing=False):
        sql_model = self.sql_model(model)

    def sql_model(self, model):
        sql_model = getattr(model, '_sql_model', None)
        if not sql_model:
            meta = model._meta
            fields = OrderedDict()
            for field in model._meta.fields.values():
                name, sql_field = self.sql_field(field)
                fields[name] = field.sql_alchemy_column()
            sql_model = DeclarativeMeta(meta.name, (object,), **fields)
            model._sql_model = sql_model
        return sql_model


