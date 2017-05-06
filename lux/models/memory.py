"""In memory model implementation
"""
from pulsar.api import Http404

from . import model
from . import query


OPERATORS = {
    'eq': lambda x, y: x == y,
    'ne': lambda x, y: x != y,
    'gt': lambda x, y: x > y,
    'ge': lambda x, y: x >= y,
    'lt': lambda x, y: x < y,
    'le': lambda x, y: x <= y
}


class Model(model.Model):

    def session(self, request):
        return Session(self, request)

    def get_query(self, session):
        return Query(self, session)


class Session(query.Session):

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def add(self, instance):
        pass

    def delete(self, instance):
        pass

    def flush(self):
        pass


class Query(query.Query):
    _data = None
    _limit = None
    _offset = None
    _filtered_data = None

    def __init__(self, model, session):
        super().__init__(model, session)
        self._filters = []
        self._sortby = []

    def __repr__(self):
        if self._data is None:
            return self.__class__.__name__
        else:
            return repr(self._data)
    __str__ = __repr__

    # Query methods
    def one(self):
        data = self.all()
        if data:
            if len(data) > 1:
                self.request.logger.error('Multiple result found for model %s.'
                                          'returning the first' % self.name)
            return data[0]
        else:
            raise Http404

    def delete(self):
        pass

    def limit(self, v):
        self._limit = v
        return self

    def offset(self, v):
        self._offset = v
        return self

    def count(self):
        return len(self.all())

    def filter_args(self, args):
        self.logger.error('Cannot filter positional arguments for '
                          'model %s.' % self.name)

    def filter_field(self, field, op, value):
        self._filtered_data = None
        if op in OPERATORS:
            self._filters.append((field, OPERATORS[op], value))
        else:
            self.logger.error('Could not apply filter %s to %s', op, self)

    def sortby_field(self, field, direction):
        self._sortby.append((field, direction))

    def all(self):
        data = self._filtered_data
        if data is None:
            self._filtered_data = data = []
            for entry in self._get_data():
                if self._filter(entry):
                    data.append(entry)

        for field, direction in self._sortby:
            if direction == 'desc':
                data = [desc(d, field) for d in data]
            else:
                data = [asc(d, field) for d in data]
            data = [s.d for s in sorted(data)]
        if self._offset:
            data = data[self._offset:]
        if self._limit:
            data = data[:self._limit]
        return data

    #  INTERNALS
    def _filter(self, entry):
        for field, op, value in self._filters:
            try:
                val = entry.get(field.name)
                if not isinstance(value, (list, tuple)):
                    value = (value,)
                if not any((op(val, v) for v in value)):
                    return False
            except Exception:
                return False
        return True

    def _get_data(self):
        raise NotImplementedError


class asc:
    __slots__ = ('d', 'value')

    def __init__(self, d, field):
        self.d = d
        self.value = d.get(field)

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        if self.value is None:
            return False
        elif other.value is None:
            return True
        else:
            return self.value < other.value

    def __gt__(self, other):
        if other.value is None:
            return False
        elif self.value is None:
            return True
        else:
            return self.value > other.value


class desc(asc):

    def __gt__(self, other):
        if self.value is None:
            return False
        elif other.value is None:
            return True
        else:
            return self.value < other.value

    def __lt__(self, other):
        if self.value is None:
            return False
        elif other.value is None:
            return True
        else:
            return self.value > other.value
