from datetime import date

from google.appengine.ext import ndb

from pulsar.utils.pep import iteritems

import lux
from lux.utils import iso8601
from lux.extensions import api


def ndbid(value):
    try:
        return int(value)
    except ValueError:
        return value


__all__ = ['ModelManager', 'ndbid']


class ModelManager(api.ModelManager):

    def get(self, request, id):
        return self.model.get_by_id(ndbid(id))

    def collection(self, request, limit, offset=0, text=None):
        if limit > 0:
            if text:
                return self.model.search(text, limit=limit, offset=offset)
            else:
                q = self.model.query()
                return q.fetch(limit)
        else:
            return []

    def instance(self, instance):
        data = {}
        for prop in instance._properties.itervalues():
            name = prop._code_name
            value = prop._get_for_dict(instance)
            if value is None:
                continue
            if hasattr(value, 'id'):
                value = value.id()
            elif isinstance(value, date):
                value = iso8601(value)
            data[name] = value
        data['id'] = instance.key.id()
        return data

    def create_model(self, request, data):
        model = self.model()
        return self.update_model(request, model, data)

    def put(self, request, instance):
        instance.put()
        return instance

    def update_model(self, request, instance, data):
        for prop in instance._properties.itervalues():
            name = prop._code_name
            if name in data:
                value = data[name]
                if name == 'id':
                    assert instance.key.id() == value
                else:
                    setattr(instance, name, value)
        return self.put(request, instance)

    def delete_model(self, request, instance):
        return instance.key.delete()
