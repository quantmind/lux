from pulsar import Http404

from lux.core import Query as BaseQuery
from lux.utils.data import as_tuple


OPERATORS = {
    'eq': lambda x, y: x == y,
    'ne': lambda x, y: x != y,
    'gt': lambda x, y: x > y,
    'ge': lambda x, y: x >= y,
    'lt': lambda x, y: x < y,
    'le': lambda x, y: x <= y
}


class Query(BaseQuery):
    _data = None
    _limit = None
    _offset = None
    _filtered_data = None

    def __init__(self, model, request):
        super().__init__(model)
        self._filters = []
        self._sortby = []
        self.request = request

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

    def limit(self, v):
        self._limit = v
        return self

    def offset(self, v):
        self._offset = v
        return self

    def count(self):
        return len(self._get_data())

    def filter_args(self, args):
        self.request.logger.error('Cannot filter positional arguments for '
                                  'model %s.' % self.name)

    def filter_field(self, field, op, value):
        self._filtered_data = None
        if op in OPERATORS:
            op = OPERATORS[op]
            if field == 'group':
                self._groups.extend(as_tuple(value))
            self._filters.append((field, op, value))
        else:
            self.request.logger.error('Could not apply filter %s to %s',
                                      op, self)

    def sortby_field(self, field, direction):
        self._sortby.append((field, direction))

    def all(self):
        data = self._get_data()
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
