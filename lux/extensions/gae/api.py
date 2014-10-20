from pulsar.apps.wsgi import Json
from pulsar.utils.pep import iteritems

import lux
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


class CRUD(api.CRUD):
    pass
