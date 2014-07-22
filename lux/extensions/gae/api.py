from pulsar.apps.wsgi import Json
from pulsar.utils.pep import iteritems

import lux
from lux import Column
from lux.extensions import api


def ndbid(value):
    try:
        return int(value)
    except ValueError:
        return value


__all__ = ['ModelManager', 'CRUD', 'ndbid']


class ModelManager(api.ModelManager):

    def get(self, id):
        return self.model.get_by_id(ndbid(id))

    def collection(self, limit, offset=0, text=None):
        if limit > 0:
            if text:
                return self.model.search(text, limit=limit, offset=offset)
            else:
                q = self.model.query()
                return q.fetch(limit)
        else:
            return []

    def instance(self, instance):
        d = {}
        for c in self.columns:
            if c.code == 'id':
                value = instance.key.id()
            else:
                value = getattr(instance, c.code, None)
            d[c.code] = value
        return d

    def create_model(self, data):
        m = self.model(**data)
        m.put()
        return m

    def update_model(self, instance, data):
        for name, value in iteritems(data):
            if name == 'id':
                assert instance.key.id() == value
            else:
                setattr(instance, name, value)
        instance.put()
        return instance

    def column(self, code):
        return Column.get(code)

    def _setup(self, columns):
        model = self.model
        if not columns:
            new_columns = [self.column('id')]
            for field in model._properties:
                new_columns.append(self.column(field))
        else:
            new_columns = []
            for col in columns:
                if not isinstance(col, Column):
                    col = Column.get(col)
                new_columns.append(col)
        self.columns = new_columns


class CRUD(api.CRUD):
    pass
